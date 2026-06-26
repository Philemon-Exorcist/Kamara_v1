// import { useEffect, useState } from 'react';

// function MyComponent() {
//   const [socket, setSocket] = useState<WebSocket | null>(null);

//   useEffect(() => {
//     // This creates the "tunnel" to Python
//     const newSocket = new WebSocket("ws://localhost:8000/ws");
    
//     // When the tunnel opens...
//     newSocket.onopen = () => console.log("We are connected!");

//     // When Python sends a message...
//     newSocket.onmessage = (event) => {
//       console.log("Python said:", event.data);
//     };

//     setSocket(newSocket);

//     // Clean up when the user leaves the page
//     return () => newSocket.close();
//   }, []);

//   const sendData = () => {
//     // Sending a message to Python
//     socket?.send("Hello from React!");
//   };

//   return <button onClick={sendData}>Click to talk to Python</button>;
// }