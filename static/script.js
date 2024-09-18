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
    
    // 清除處理好的檔案並還原按鈕樣式
    const downloadButton = document.getElementById('downloadButton');
    downloadButton.disabled = true;
    downloadButton.classList.remove('completed');
    downloadButton.onclick = null;
});

document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    document.getElementById('loading').style.display = 'block';

    // 使用 FileReader 讀取檔案並轉為字串
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

    // 讀取所有檔案並傳遞給後端
    Promise.all([readFileContent(file1), readFileContent(file2), readFileContent(template)])
        .then(([file1Content, file2Content, templateContent]) => {
            const payload = {
                file1: file1Content,
                file2: file2Content,
                template: templateContent
            };

            return fetch('https://gcpaccount.zeabur.app/process', { // 使用後端的 process 路徑
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
        })
        .then(response => {
            document.getElementById('loading').style.display = 'none';
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const downloadButton = document.getElementById('downloadButton');
                downloadButton.disabled = false;
                downloadButton.classList.add('completed'); 

                // 顯示處理好的資料
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
