
fetch('data.json')
  .then(response => response.json())
  .then(data => {
    const container = document.getElementById('news-container');
    data.forEach(item => {
      const div = document.createElement('div');
      div.className = 'news-card';
      div.innerHTML = `
        <h2>${item.title}</h2>
        <p><strong>来源：</strong> ${item.source}</p>
        <p><strong>摘要：</strong> ${item.summary}</p>
        <a href="${item.url}" target="_blank">查看原文</a>
      `;
      container.appendChild(div);
    });
  });
