console.log("main.js script started");

fetch('/api/simulate')
    .then(response => {
        console.log("Fetch response received:", response);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log("Data received and parsed:", data);
        renderChart(data.chart_data);
        renderLedger(data.ledger);
        renderPerformance(data.performance);
        console.log("Rendering functions called");
    })
    .catch(error => console.error('Fetch error:', error));

function renderChart(chartData) {
    const ctx = document.getElementById('stockChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Stock Price',
                    data: chartData.prices,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    fill: false
                },
                {
                    label: '7-Day MA',
                    data: chartData.ma7,
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 1,
                    fill: false
                },
                {
                    label: '30-Day MA',
                    data: chartData.ma30,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    fill: false
                }
            ]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'month'
                    }
                }
            }
        }
    });
}

function renderLedger(ledgerData) {
    const tableBody = document.getElementById('ledgerTable').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = ''; // Clear existing rows
    ledgerData.forEach(trade => {
        let row = tableBody.insertRow();
        row.insertCell(0).innerText = trade.date || '';
        row.insertCell(1).innerText = trade.action || '';
        row.insertCell(2).innerText = trade.shares !== null ? trade.shares.toFixed(2) : 'N/A';
        row.insertCell(3).innerText = trade.price !== null ? trade.price.toFixed(2) : 'N/A';
    });
}

function renderPerformance(performanceData) {
    const performanceDiv = document.getElementById('performance');
    performanceDiv.innerHTML = `
        <h2>Portfolio Performance</h2>
        <p>Initial Capital: $${performanceData.initial_capital.toFixed(2)}</p>
        <p>Final Value: $${performanceData.final_value.toFixed(2)}</p>
        <p>Total Return: ${performanceData.returns_pct.toFixed(2)}%</p>
    `;
}
