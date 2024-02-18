// import { Route, Routes } from 'react-router-dom';
// import Navbar from './components/Navbar';
// import Camera from './components/Camera';
// import CamTimeline from './components/CamTimeline';
// import styles from './style';
// import Feed1 from './components/Feed1';
// import Feed1Settings from './components/Feed1Settings';

// const App = () => (
//   <div className="bg-primary w-full overflow-hidden">
//     <div className={`${styles.paddingX} ${styles.flexCenter}`}>
//       <div className={`${styles.boxWidth}`}>
//         <Navbar />
//         <Routes>
//           <Route path="/camera" element={<Camera />} />
//           <Route path="/timeline" element={<CamTimeline />} />
//           <Route path="/camera1" element={<Feed1 />} />
//           <Route path="/camera1/settings" element={<Feed1Settings />} />
//           <Route path="/camera2" element={<Feed1 />} />
//           <Route path="/camera3" element={<Feed1 />} />
//           <Route path="/camera4" element={<Feed1 />} />
//           <Route path="/camera5" element={<Feed1 />} />
//           <Route path="/camera6" element={<Feed1 />} />
//         </Routes>
//       </div>
//     </div>
//   </div>
// );
// export default App

// import React, { useState, useEffect } from 'react';

// function App() {
//   const [imageData, setImageData] = useState(null);
//   const [data, setData] = useState(null);
//   function SendStatus() {
//     fetch('http://localhost:8080/get_img_for_cam/172.19.0.2')
//       .then(response => response.json())
//       .then(json => setData(json))
//       .catch(error => console.error(error));
//   }
//   useEffect(() => {
//     // Function to fetch image data
//     const fetchImageData = async () => {
//       try {
//         const response = await fetch('http://localhost:8080/get_img_for_cam/172.19.0.2', {
//           method: 'POST',
//           headers: {
//             'Content-Type': 'application/json'
//           },
//           // body: JSON.stringify({ ip: 'your_ip_here' }) // Replace 'your_ip_here' with the actual IP
//         });
//         if (response.ok) {
//           const data = await response.json();
//           setImageData(data);
//         } else {
//           console.error('Failed to fetch image data');
//         }
//       } catch (error) {
//         console.error('Error fetching image data:', error);
//       }
//     };

//     // Call the function to fetch image data
//     fetchImageData();
//   }, []); // Empty dependency array to run the effect only once

//   return (
//     <div>
//       {SendStatus}
//       {/* {imageData && ( */}
//       {/* <img src={imageData.src} alt="Camera Image" /> */}
//       {/* <p>{data}</p>
//                 <p>Time: {data}</p> */}
//       <div style={{ fontSize: '18px' }}><pre>{JSON.stringify(data, null, 2)}</pre></div>
//       {/* )} */}
//     </div>
//   );
// }

// export default App;