// STEP 1: get elements
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');

// STEP 2: start camera
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        console.error("Camera error:", err);
    }
}

// STEP 3: capture image
function captureImage() {
    const context = canvas.getContext('2d');

    // match canvas size with video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // draw current frame from video
    context.drawImage(video, 0, 0);

    // convert image → base64 string
    const imageData = canvas.toDataURL('image/jpeg');

    // send to backend
    sendImage(imageData);
}

// STEP 4: send to backend
async function sendImage(imageData) {
    try {
        const response = await fetch('/login-face', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageData })
        });

        const data = await response.json();

        if (data.success) {
            window.location.href = `/lobby`;
        } else {
            alert("Face not recognized");
        }

    } catch (err) {
        console.error("Error sending image:", err);
    }
}

// STEP 5: start camera automatically
startCamera();