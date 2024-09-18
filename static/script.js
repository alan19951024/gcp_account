document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    document.getElementById('loading').style.display = 'block';

    const file1 = document.getElementById('file1').files[0];
    const file2 = document.getElementById('file2').files[0];
    const template = document.getElementById('template').files[0];

    const readFileContent = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(reader.error);
            reader.readAsText(file);
        });
    };

    Promise.all([readFileContent(file1), readFileContent(file2), readFileContent(template)])
        .then(([file1Content, file2Content, templateContent]) => {
            const payload = {
                file1: file1Content,
                file2: file2Content,
                template: templateContent
            };

            return fetch('https://gcpaccount.zeabur.app/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
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
        })
        .catch(error => {
            document.getElementById('loading').style.display = 'none';
            console.error('Error:', error);
            alert('檔案處理失敗: ' + error.message);
        });
});
