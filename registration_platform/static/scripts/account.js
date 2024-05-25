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

async function uploadFile(documentFormData) {
    const response = await fetch('/verification/upload-document/', {
            method: 'POST',
            body: documentFormData
        });
    const document_id = documentFormData.get('document_id').split('-')[1];
    const result = await response.json();
    if (response.ok) {
        console.log('File uploaded successfully', result);
    } else {
        console.log('Error uploading file:', result.message);
        console.log(`status-${document_id}`)
        let statusElement = document.getElementById(`status-${document_id}`);
        if (statusElement) {
            statusElement.innerText = `Error: ${result.message}`;
        }
    }
}


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

            uploadFile(documentFormData)
        }
    };

    const fileInputs = document.querySelectorAll('.file-upload');
    console.log(`Found ${fileInputs.length} file inputs`);

    fileInputs.forEach(input => {
        input.addEventListener('change', handleFileUpload);
        console.log(`Event listener attached to input ${input.id}`);
    });
});
