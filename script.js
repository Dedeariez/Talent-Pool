// Link CSV milik Akang yang sudah dipublish
const CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTg3rjqHoD36dUM0PU33sGqYnovngVpCfBS6A2EYngYMeU8vuvXLRRuD_Dd8utXGckTMKQB_IKtqW5H/pub?output=csv";

let talents = [];
let currentFilter = "all";

// Fungsi untuk memperbaiki link audio agar bisa langsung diputar
function fixLink(url) {
    if (!url || url.trim() === "" || url.trim() === "-") return null;
    let link = url.trim();
    
    // Perbaikan Dropbox
    if (link.includes("dropbox.com")) {
        link = link.replace("www.dropbox.com", "dl.dropboxusercontent.com")
                   .replace(/\?dl=[01]/, "?raw=1")
                   .replace("&dl=0", "&raw=1");
        if (!link.includes("raw=1")) link += (link.includes("?") ? "&" : "?") + "raw=1";
        return link;
    }
    
    // Perbaikan Google Drive
    if (link.includes("drive.google.com")) {
        const match = link.match(/[?&]id=([^&]+)/) || link.match(/\/d\/(.*?)\//) || link.match(/\/file\/d\/(.*?)$/);
        if (match) return `https://docs.google.com/uc?export=open&id=${match[1].split(/[?&/]/)[0]}`;
    }
    return link;
}

// Fungsi filter yang dipanggil dari tombol HTML
window.setFilter = function(g) {
    currentFilter = g;
    document.querySelectorAll('.tab-btn').forEach(b => {
        const isMatch = b.getAttribute('onclick').includes(`'${g}'`);
        b.classList.toggle('active', isMatch);
    });
    render();
};

function render() {
    const grid = document.getElementById("talentGrid");
    const search = document.getElementById("searchInput").value.toLowerCase();
    
    if (!grid) return;
    grid.innerHTML = "";

    const filtered = talents.filter(t => {
        const matchFilter = (currentFilter === "all" || t.gender === currentFilter);
        const matchSearch = t.name.toLowerCase().includes(search);
        return matchFilter && matchSearch;
    });

    if (filtered.length === 0) {
        grid.innerHTML = "<div class='loading'>Talent tidak ditemukan.</div>";
        return;
    }

    filtered.forEach(t => {
        const div = document.createElement("div");
        div.className = "card";
        
        let audioHTML = t.samples.map((link, i) => `
            <div class="audio-item">
                <label>Audio Sample ${i + 1}</label>
                <audio controls preload="none">
                    <source src="${link}" type="audio/mpeg">
                </audio>
            </div>
        `).join("");

        div.innerHTML = `
            <div class="card-header">
                <h3>${t.name}</h3>
                <span class="tag">${t.gender}</span>
            </div>
            <span class="category-label">${t.displayGender}</span>
            <div class="samples-container">
                ${audioHTML}
            </div>
        `;
        grid.appendChild(div);
    });

    // Auto-stop audio lain saat satu audio di-play
    const players = document.querySelectorAll("audio");
    players.forEach(p => p.addEventListener("play", () => {
        players.forEach(other => { if(other !== p) other.pause(); });
    }));
}

async function loadData() {
    console.log("Mengambil data...");
    const grid = document.getElementById("talentGrid");
    
    try {
        const res = await fetch(CSV_URL);
        if (!res.ok) throw new Error("Gagal akses data CSV.");
        
        const text = await res.text();
        const rows = text.split(/\r?\n/).filter(r => r.trim() !== "");
        
        // Lewati baris pertama (judul kolom)
        talents = rows.slice(1).map(row => {
            // Split CSV dengan aman jika ada koma di dalam teks (pake regex)
            const cols = row.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/).map(c => c.replace(/"/g, "").trim());
