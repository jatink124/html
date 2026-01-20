const express = require('express');
const path = require('path');
const cors = require('cors');
const bodyParser = require('body-parser');
const mysql = require('mysql2');

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public')); // Serves HTML files from 'public' folder

// --- DATABASE CONNECTION ---
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '', 
    database: 'market_analysis_db'
});

db.connect((err) => {
    if (err) console.error('DB Connection Error:', err);
    else console.log('✅ Connected to MySQL Database');
});

// --- PAGE ROUTES ---
// Serve the Dashboard as the main entry point
app.get('/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});
// Add this to server.js
app.get('/view', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'view.html'));
});

// --- API ROUTE 1: GET ALL REPORTS (For Dashboard/View) ---
app.get('/api/reports', (req, res) => {
    const query = `
        SELECT r.report_id, r.report_date, r.title, r.overall_strategy,
               i.entity_name, i.event_details, i.layman_explanation
        FROM analysis_reports r
        LEFT JOIN analysis_items i ON r.report_id = i.report_id
        ORDER BY r.report_date DESC, r.report_id DESC
    `;

    db.query(query, (err, results) => {
        if (err) return res.status(500).send(err);
        const reports = {};
        results.forEach(row => {
            if (!reports[row.report_id]) {
                reports[row.report_id] = {
                    id: row.report_id,
                    date: row.report_date,
                    title: row.title,
                    strategy: row.overall_strategy,
                    items: []
                };
            }
            if (row.entity_name) {
                reports[row.report_id].items.push({
                    name: row.entity_name,
                    details: row.event_details,
                    explanation: row.layman_explanation
                });
            }
        });
        res.json(Object.values(reports));
    });
});

// --- API ROUTE 2: GET SINGLE REPORT (For Editing) ---
app.get('/api/reports/:id', (req, res) => {
    const reportId = req.params.id;
    const query = `
        SELECT r.report_id, r.report_date, r.title, r.overall_strategy,
               i.entity_name, i.event_details, i.layman_explanation
        FROM analysis_reports r
        LEFT JOIN analysis_items i ON r.report_id = i.report_id
        WHERE r.report_id = ?
    `;

    db.query(query, [reportId], (err, results) => {
        if (err) return res.status(500).send(err);
        if (results.length === 0) return res.status(404).send("Report not found");

        const report = {
            id: results[0].report_id,
            date: results[0].report_date,
            title: results[0].title,
            strategy: results[0].overall_strategy,
            items: []
        };

        results.forEach(row => {
            if (row.entity_name) {
                report.items.push({
                    entity_name: row.entity_name,
                    event_details: row.event_details,
                    layman_explanation: row.layman_explanation
                });
            }
        });
        res.json(report);
    });
});

// --- API ROUTE 3: CREATE REPORT ---
app.post('/api/reports', (req, res) => {
    const { report_date, title, overall_strategy, items } = req.body;
    const sqlReport = "INSERT INTO analysis_reports (report_date, title, overall_strategy) VALUES (?, ?, ?)";
    
    db.query(sqlReport, [report_date, title, overall_strategy], (err, result) => {
        if (err) return res.status(500).send("Error saving report");
        const newReportId = result.insertId;
        saveItems(newReportId, items, res);
    });
});

// --- API ROUTE 4: UPDATE REPORT ---
app.put('/api/reports/:id', (req, res) => {
    const reportId = req.params.id;
    const { report_date, title, overall_strategy, items } = req.body;

    const sqlUpdate = "UPDATE analysis_reports SET report_date=?, title=?, overall_strategy=? WHERE report_id=?";
    
    db.query(sqlUpdate, [report_date, title, overall_strategy, reportId], (err) => {
        if (err) return res.status(500).send("Error updating report");

        // Delete old items and re-insert new ones (simplest update strategy)
        db.query("DELETE FROM analysis_items WHERE report_id = ?", [reportId], (err) => {
            if (err) return res.status(500).send("Error clearing old items");
            saveItems(reportId, items, res);
        });
    });
});

// --- API ROUTE 5: DELETE REPORT ---
app.delete('/api/reports/:id', (req, res) => {
    const reportId = req.params.id;
    // Delete items first to maintain referential integrity (if no cascade set)
    db.query("DELETE FROM analysis_items WHERE report_id = ?", [reportId], (err) => {
        if (err) return res.status(500).send("Error deleting items");
        
        db.query("DELETE FROM analysis_reports WHERE report_id = ?", [reportId], (err) => {
            if (err) return res.status(500).send("Error deleting report");
            res.json({ message: "Deleted successfully" });
        });
    });
});

// Helper function to save items
function saveItems(reportId, items, res) {
    if (items && items.length > 0) {
        const itemValues = items.map(item => [
            reportId, item.entity_name, item.event_details, item.layman_explanation
        ]);
        const sqlItems = "INSERT INTO analysis_items (report_id, entity_name, event_details, layman_explanation) VALUES ?";
        
        db.query(sqlItems, [itemValues], (err) => {
            if (err) return res.status(500).send("Error saving items");
            res.status(200).send({ message: "Success" });
        });
    } else {
        res.status(200).send({ message: "Success (No items)" });
    }
}

app.listen(3000, () => {
    console.log('Server running at http://localhost:3000/dashboard');
});