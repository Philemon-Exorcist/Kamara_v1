import { useCallback, useEffect, useRef } from 'react';
import {
  type Editor,
  type TLGeoShape,
  type TLShapeId,
  Tldraw,
  createShapeId,
  toRichText,
} from 'tldraw';
import 'tldraw/tldraw.css';
import { getGeneratedCourseStorageKey } from '../course-api';

const WS_BASE_URL =
  typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'ws://localhost:8001/ws/api/v1'
    : 'wss://kamsi-xza9.onrender.com/ws/api/v1';

type BoardCommand =
  | {
      action: 'draw_shape';
      data: {
        id: string;
        shape: string;
        x: number;
        y: number;
        width: number;
        height: number;
      };
    }
  | {
      action: 'write_text';
      data: {
        id: string;
        text: string;
        x: number;
        y: number;
      };
    }
  | {
      action: 'move_shape';
      data: {
        shapeId: string;
        x: number;
        y: number;
      };
    }
  | {
      action: 'resize_item';
      data: {
        shapeId: string;
        width: number;
        height: number;
      };
    }
  | {
      action: 'delete_shape';
      data: {
        shapeId: string;
      };
    }
  | {
      action: 'clear_board';
    };

type TldrawComponentProps = {
  sessionId?: string;
  onEditorReady?: (editor: Editor | null) => void;
};

function getSessionId(fallback?: string) {
  if (fallback) return fallback;
  if (typeof window === 'undefined') return null;

  const params = new URLSearchParams(window.location.search);
  if (params.get('session_id')) {
    return params.get('session_id');
  }

  const activeSessionId = localStorage.getItem('active_session_id');
  if (activeSessionId) {
    return activeSessionId;
  }

  const storedCourse = sessionStorage.getItem(getGeneratedCourseStorageKey());
  if (!storedCourse) {
    return null;
  }

  try {
    const parsedCourse = JSON.parse(storedCourse) as { session_id?: string; generatedCourse?: { session_id?: string; data?: { session_id?: string } } };
    return parsedCourse.generatedCourse?.session_id ?? parsedCourse.generatedCourse?.data?.session_id ?? parsedCourse.session_id ?? null;
  } catch {
    return null;
  }
}

function getShapeId(id: string): TLShapeId {
  return id.startsWith('shape:') ? (id as TLShapeId) : createShapeId(id);
}

function getGeoShape(shape: string): TLGeoShape['props']['geo'] {
  switch (shape) {
    case 'circle':
    case 'ellipse':
      return 'ellipse';
    case 'triangle':
      return 'triangle';
    case 'diamond':
      return 'diamond';
    case 'rectangle':
    case 'rect':
    case 'square':
    default:
      return 'rectangle';
  }
}

function applyBoardCommand(editor: Editor, command: BoardCommand) {
  switch (command.action) {
    case 'draw_shape': {
      const id = getShapeId(command.data.id);

      editor.createShape({
        id,
        type: 'geo',
        x: command.data.x,
        y: command.data.y,
        props: {
          geo: getGeoShape(command.data.shape),
          w: command.data.width,
          h: command.data.height,
          fill: 'none',
          color: 'blue',
          richText: toRichText(''),
        },
      });
      break;
    }

    case 'write_text': {
      const id = getShapeId(command.data.id.replace(/^text:/, 'text-'));

      editor.createShape({
        id,
        type: 'text',
        x: command.data.x,
        y: command.data.y,
        props: {
          richText: toRichText(command.data.text),
          autoSize: true,
          color: 'black',
        },
      });
      break;
    }

    case 'move_shape': {
      const id = getShapeId(command.data.shapeId);
      const shape = editor.getShape(id);
      if (shape) {
        editor.updateShape({ id, type: shape.type, x: command.data.x, y: command.data.y });
      }
      break;
    }

    case 'resize_item': {
      const id = getShapeId(command.data.shapeId);
      const shape = editor.getShape(id);
      if (shape?.type === 'geo') {
        editor.updateShape({
          id,
          type: 'geo',
          props: {
            w: command.data.width,
            h: command.data.height,
          },
        });
      }
      break;
    }

    case 'delete_shape': {
      const id = getShapeId(command.data.shapeId);
      if (editor.getShape(id)) {
        editor.deleteShapes([id]);
      }
      break;
    }

    case 'clear_board': {
      editor.deleteShapes([...editor.getCurrentPageShapeIds()]);
      break;
    }
  }
}

const TldrawComponent = ({ sessionId, onEditorReady }: TldrawComponentProps) => {
  const socketRef = useRef<WebSocket | null>(null);
  const editorRef = useRef<Editor | null>(null);

  const disconnectBoardSocket = useCallback(() => {
    onEditorReady?.(null);
    editorRef.current = null;

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ action: 'end_session' }));
    }

    socketRef.current?.close();
    socketRef.current = null;
  }, []);

  const connectBoardSocket = useCallback(() => {
    const editor = editorRef.current;
    const token = localStorage.getItem('access_token');
    const activeSessionId = getSessionId(sessionId);

    if (!editor || !token || !activeSessionId || socketRef.current) {
      return;
    }

    const socket = new WebSocket(`${WS_BASE_URL}/live?token=${encodeURIComponent(token)}`);
    socketRef.current = socket;

    socket.addEventListener('open', () => {
      socket.send(
        JSON.stringify({
          action: 'start_session',
          session_id: activeSessionId,
        })
      );
    });

    socket.addEventListener('message', (event) => {
      if (typeof event.data !== 'string') {
        return;
      }

      try {
        const payload = JSON.parse(event.data) as Partial<BoardCommand> & { type?: string; action?: string };

        if (!payload || typeof payload !== 'object' || !('action' in payload)) {
          return;
        }

        if (
          payload.action !== 'draw_shape' &&
          payload.action !== 'write_text' &&
          payload.action !== 'move_shape' &&
          payload.action !== 'resize_item' &&
          payload.action !== 'delete_shape' &&
          payload.action !== 'clear_board'
        ) {
          return;
        }

        applyBoardCommand(editor, payload as BoardCommand);
      } catch (error) {
        console.error('Could not apply tutor board command', error);
      }
    });
  }, [sessionId]);

  const handleMount = useCallback(
    (editor: Editor) => {
      editorRef.current = editor;
      onEditorReady?.(editor);
      connectBoardSocket();
    },
    [connectBoardSocket, onEditorReady]
  );

  useEffect(() => {
    connectBoardSocket();

    return () => {
      disconnectBoardSocket();
    };
  }, [connectBoardSocket, disconnectBoardSocket, sessionId]);

  return (
    <div style={{ width: '100%', height: '100%', minHeight: 400 }}>
      <Tldraw onMount={handleMount} />
    </div>
  );
};

export default TldrawComponent;
