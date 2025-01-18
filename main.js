let db;

async function initDB() {
    // Initialize SQL.js
    const SQL = await initSqlJs({
        locateFile: file => `https://sql.js.org/dist/${file}`
    });
    
    db = new SQL.Database();
    
    // Create table structure
    db.run(`CREATE TABLE IF NOT EXISTS breaches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_count INTEGER,
        dump_name TEXT,
        breach_date TEXT,
        info TEXT,
        source TEXT
    )`);
    
    // Load data
    await getDatasets();
}

async function getDatasets() {
    try {
        const response = await fetch("datasets/combined.json");
        const data = await response.json();
        
        // Begin transaction for bulk insert
        db.run("BEGIN TRANSACTION");
        
        const stmt = db.prepare(`
            INSERT INTO breaches (record_count, dump_name, breach_date, info, source)
            VALUES (?, ?, ?, ?, ?)
        `);
        
        data.forEach(item => {
            // Sanitize and provide default values for all fields
            const record_count = parseInt(item.record_count) || 0;
            const dump_name = item.dump_name || 'Unknown';
            const breach_date = item.breach_date || 'N/A';
            const info = item.info || 'N/A';
            const source = item.source || 'Unknown';
            
            stmt.run([
                record_count,
                dump_name,
                breach_date,
                info,
                source
            ]);
        });
        
        stmt.free();
        db.run("COMMIT");
        
        // Initial table display
        updateTable();
        
        // Initialize DataTables with server-side processing
        initializeDataTable();
        
    } catch (error) {
        console.error('Error loading data:', error);
        // Show error message to user
        const tableDiv = document.getElementById('breach_div');
        tableDiv.innerHTML = `<div class="alert alert-danger">Error loading data: ${error.message}</div>`;
    }
}

function initializeDataTable() {
    $('#breach_table').DataTable({
        serverSide: true,
        processing: true,
        pageLength: 25,
        order: [[0, 'desc']], // Default sort by record count descending
        ajax: function(data, callback, settings) {
            // Get current page, search term, and sort info
            const searchTerm = data.search.value;
            const page = data.start / data.length + 1;
            const pageSize = data.length;
            
            // Handle sorting
            const sortColumn = data.order.map(order => {
                const columnIndex = order.column;
                const columnName = [
                    'record_count',
                    'dump_name',
                    'breach_date',
                    'info',
                    'source'
                ][columnIndex];
                const direction = order.dir.toUpperCase();
                return `${columnName} ${direction}`;
            }).join(', ');
            
            // Build SQL query
            let whereClause = searchTerm ? 
                `WHERE dump_name LIKE '%${searchTerm}%' 
                OR info LIKE '%${searchTerm}%' 
                OR source LIKE '%${searchTerm}%'` : '';
            
            let orderClause = sortColumn ? `ORDER BY ${sortColumn}` : '';
            
            // Get total count
            const totalResult = db.exec(`
                SELECT COUNT(*) as count 
                FROM breaches ${whereClause}`
            )[0].values[0][0];
            
            // Get paginated and sorted data
            const result = db.exec(`
                SELECT record_count, dump_name, breach_date, info, source 
                FROM breaches 
                ${whereClause}
                ${orderClause}
                LIMIT ${pageSize} 
                OFFSET ${(page - 1) * pageSize}`
            )[0];
            
            const formattedData = result.values.map(row => {
                return [
                    new Intl.NumberFormat().format(row[0]),
                    row[1],
                    row[2],
                    row[3],
                    row[4]
                ];
            });
            
            callback({
                draw: data.draw,
                recordsTotal: totalResult,
                recordsFiltered: totalResult,
                data: formattedData
            });
        },
        columns: [
            { 
                data: 0,
                type: 'num',  // Ensures proper numeric sorting
                render: function(data) {
                    return data;  // Already formatted in formattedData
                }
            },
            { data: 1 },
            { data: 2 },
            { data: 3 },
            { data: 4 }
        ]
    });
}

function updateTable() {
    const tableDiv = document.getElementById('breach_div');
    tableDiv.innerHTML = `
        <table id="breach_table" class="table table-bordered table-hover table-striped">
            <thead>
                <tr>
                    <th scope="col">Record Count</th>
                    <th scope="col">Name</th>
                    <th scope="col">Dump Date</th>
                    <th scope="col">Info</th>
                    <th scope="col">Source</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    `;
}