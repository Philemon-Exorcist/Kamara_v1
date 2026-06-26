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
    <div className="live-classroom-area" style={{ width: '100%', height: '100%' }}>
      <div className="classroom-header">
        <h2>Interactive Whiteboard</h2>
      </div>
      <TldrawComponent />
    </div>
  );
}