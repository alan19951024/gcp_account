document.getElementById('file1Button').addEventListener('click', function() {
    document.getElementById('file1').click();
});

document.getElementById('file1').addEventListener('change', function() {
    document.getElementById('file1Name').textContent = this.files[0].name;
});

document.getElementById('file2Button').addEventListener('click', function() {
    document.getElementById('file2').click();
});

document.getElementById('file2').addEventListener('change', function() {
    document.getElementById('file2Name').textContent = this.files[0].name;
});

document.getElementById('templateButton').addEventListener('click', function() {
    document.getElementById('template').click();
});

document.getElementById('template').addEventListener('change', function() {
    document.getElementById('templateName').textContent = this.files[0].name;
});

document.getElementById('clearButton').addEventListener('click', function() {
    document.getElementById('file1').value = '';
    document.getElementById('file1Name').textContent = '';
    document.getElementById('file2').value = '';
    document.getElementById('file2Name').textContent = '';
    document.getElementById('template').value = '';
    document.getElementById('templateName').textContent = '';
    
    const downloadButton = document.getElementById('downloadButton');
    downloadButton.disabled = true;
    downloadButton.classList.remove('completed');
    downloadButton.onclick = null;
});

function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(file);
    });
}

document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    document.getElementById('loading').style.display = 'block';

    try {
        const file1 = document.getElementById('file1').files[0];
        const file2 = document.getElementById('file2').files[0];
        const template = document.getElementById('template').files[0];

        const [file1Content, file2Content, templateContent] = await Promise.all([
            readFileAsBase64(file1),
            readFileAsBase64(file2),
            readFileAsBase64(template)
        ]);

        const payload = {
            file1: file1Content,
            file2: file2Content,
            template: templateContent
        };

        const response = await fetch('https://gcpaccount.zeabur.app/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        document.getElementById('loading').style.display = 'none';

        if (data.success) {
            const downloadButton = document.getElementById('downloadButton');
            downloadButton.disabled = false;
            downloadButton.classList.add('completed'); 

            downloadButton.onclick = function() {
                const link = document.createElement('a');
                const blob = new Blob([data.result], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                link.href = url;
                link.download = 'processed_data.csv';
                link.click();
            };
        } else {
            alert('檔案處理失敗: ' + data.message);
        }
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        console.error('Error:', error);
        alert('檔案處理失敗: ' + error.message);
    }
});
