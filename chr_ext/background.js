chrome.action.onClicked.addListener((tab) => {
    if (tab.id) {
        fetchContentAndInject(tab);
    }
});

function fetchContentAndInject(tab) {
    fetch('http://localhost:8081/extract-content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ url: tab.url })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server response: ${response.status} ${response.statusText}`);
        }
        return response.text();
    })
    .then(data => {
        chrome.scripting.executeScript({
            target: {tabId: tab.id},
            func: replaceContent,
            args: [data]
        });
    })
    .catch(error => {
        console.error('Error:', error);
        alertUser(error.message, tab.id);
    });
}

function replaceContent(newContent) {
    document.open();
    document.write(newContent);
    document.close();
}

function alertUser(message, tabId) {
    chrome.scripting.executeScript({
        target: {tabId: tabId},
        func: showAlert,
        args: [message]
    });
}

function showAlert(message) {
    const errorContainerId = 'chrome-extension-error-container';
    if (!document.getElementById(errorContainerId)) {
        const container = document.createElement('div');
        container.id = errorContainerId;
        container.style.position = 'fixed';
        container.style.left = '0';
        container.style.top = '0';
        container.style.width = '100%';
        container.style.backgroundColor = 'red';
        container.style.color = 'white';
        container.style.textAlign = 'center';
        container.style.zIndex = '1000';
        container.style.padding = '10px';
        container.style.fontSize = '16px';
        container.innerHTML = `
            <p style="margin-bottom: 20px;">${message}</p>
            <p style="margin-bottom: 20px;"><strong>Check if the FastAPI backend server is running and accessible.</strong></p>
            <button onclick="document.getElementById('${errorContainerId}').remove()" style="margin-top: 20px;">Dismiss</button>
        `;

        document.body.prepend(container);
    }
}


