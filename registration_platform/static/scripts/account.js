let ws_url = `ws://${window.location.host}/ws/document-status/`
const statusSocket = new WebSocket(ws_url);

statusSocket.onmessage = function(event) {
    let data = JSON.parse(event.data);
    console.log(`Event: ${data.document_id} ${data.new_status}`)
    let statusElement = document.getElementById(`status-${data.document_id}`);
    if (statusElement) {
        statusElement.innerText = data.new_status;
    }
};

document.addEventListener('DOMContentLoaded', () => {

    const handleFileUpload = async (event) => {
        console.log('handleFileUpload called');
        const fileInput = event.target;
        const file = fileInput.files[0];
        if (file) {
            console.log(`File selected: ${file.name} from input ${fileInput.id} ${fileInput.name}`);

            const documentFormData = new FormData();
            documentFormData.append('document_id', fileInput.id);
            documentFormData.append('file', file);
            documentFormData.append('csrfmiddlewaretoken', window.CSRF_TOKEN);

            statusSocket.send(JSON.stringify({
                'document_id': fileInput.id,
            }))

            // Отправка файла на сервер с помощью Fetch API
            try {
                const response = await fetch('/verification/upload-document/', {
                    method: 'POST',
                    body: documentFormData
                });
                const result = await response.json();
                console.log('File uploaded successfully', result);
            } catch (error) {
                console.error('Error uploading file:', error);
            }
        }
    };

    const fileInputs = document.querySelectorAll('.file-upload');
    console.log(`Found ${fileInputs.length} file inputs`);

    fileInputs.forEach(input => {
        input.addEventListener('change', handleFileUpload);
        console.log(`Event listener attached to input ${input.id}`);
    });
});
