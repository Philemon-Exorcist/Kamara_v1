import TldrawComponent from "../pages/dash-component/tldraw";

/**
 * LiveClassroom Component
 * 
 * This component serves as the interactive whiteboard area for the 
 * Kamara AI classroom, integrating the Tldraw component for 
 * real-time visual learning.
 */
export function LiveClassroom() {
  return (
    <div
      className="live-classroom-area"
      style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', minHeight: 0 }}
    >
      <div className="classroom-header">
        <h2>Interactive Whiteboard</h2>
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>
        <TldrawComponent />
      </div>
    </div>
  );
}
