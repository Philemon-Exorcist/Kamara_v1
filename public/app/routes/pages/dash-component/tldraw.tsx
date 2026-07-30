import { useCallback, useEffect, useRef } from 'react';
import {
  type Editor,
  type IndexKey,
  type TLGeoShape,
  type TLShapeId,
  Tldraw,
  createShapeId,
  toRichText,
} from 'tldraw';
import 'tldraw/tldraw.css';
import { getGeneratedCourseStorageKey } from '../genie-api';

const WS_BASE_URL =
  typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'ws://localhost:8001/ws/api/v1'
    : 'wss://kamsi-t57w.onrender.com/ws/api/v1';
// will add cloud run url 
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
    }
  | {
      action: 'draw_line';
      data: {
        id: string;
        x: number;
        y: number;
        line_type?: string;
      };
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

    case 'draw_line': {
      const id = getShapeId(command.data.id);
      const lineType = command.data.line_type ?? (command.data as { type?: string }).type;
      const isCurve = lineType === 'curve';

      editor.createShape({
        id,
        type: 'line',
        x: command.data.x,
        y: command.data.y,
        props: {
          color: 'blue',
          dash: 'solid',
          size: 'm',
          spline: isCurve ? 'cubic' : 'line',
          points: {
            start: { id: 'start', index: 'a1' as IndexKey, x: 0, y: 0 },
            end: { id: 'end', index: 'a2' as IndexKey, x: isCurve ? 180 : 140, y: isCurve ? 80 : 0 },
          },
          scale: 1,
        },
      });
      break;
    }
  }
}

function executeCanvasScript(editor: Editor, javascriptCode: string) {
  if (!javascriptCode.trim()) {
    return;
  }

  try {
    const runner = new Function("editor", javascriptCode);
    runner(editor);
  } catch (error) {
    console.error("Could not execute canvas JavaScript:", error);
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
    const currentSocket = socketRef.current;

    if (!editor || !token || !activeSessionId) {
      return;
    }

    if (currentSocket?.readyState === WebSocket.OPEN || currentSocket?.readyState === WebSocket.CONNECTING) {
      return;
    }

    if (currentSocket) {
      currentSocket.close();
      socketRef.current = null;
    }

    const socket = new WebSocket(
      `${WS_BASE_URL}/live?token=${encodeURIComponent(token)}&session_id=${encodeURIComponent(activeSessionId)}`
    );
    socketRef.current = socket;

    socket.addEventListener('open', () => {
      socket.send(
        JSON.stringify({
          action: 'start_session',
          session_id: activeSessionId,
        })
      );
    });

    socket.addEventListener('close', () => {
      if (socketRef.current === socket) {
        socketRef.current = null;
      }
    });

    socket.addEventListener('error', () => {
      if (socketRef.current === socket) {
        socketRef.current = null;
      }
    });

    socket.addEventListener('message', (event) => {
      if (typeof event.data !== 'string') {
        return;
      }

      try {
        const payload = JSON.parse(event.data) as Partial<BoardCommand> & {
          type?: string;
          action?: string;
          payload?: Partial<BoardCommand>;
        };

        const command =
          payload && typeof payload === 'object' && typeof payload.action === 'string'
            ? payload
            : payload?.payload;

        if (!command || typeof command.action !== 'string') {
          return;
        }

        if (
          command.action !== 'draw_shape' &&
          command.action !== 'write_text' &&
          command.action !== 'move_shape' &&
          command.action !== 'resize_item' &&
          command.action !== 'delete_shape' &&
          command.action !== 'clear_board' &&
          command.action !== 'draw_line'
        ) {
          if (payload.type === 'exec_js') {
            const execPayload = payload as { code?: string; javascript_code?: string };
            executeCanvasScript(editor, String(execPayload.code ?? execPayload.javascript_code ?? ''));
          }
          return;
        }

        applyBoardCommand(editor, command as BoardCommand);
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
    <div style={{ width: '100%', height: '100%', minHeight: 400, background: '#fff' }}>
      <Tldraw hideUi onMount={handleMount} />
    </div>
  );
};

export default TldrawComponent;
