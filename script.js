// GANTI LINK DI BAWAH INI dengan Link "Publish to Web" (Langkah 1 di atas)
const CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1T7vE3K7xU_77v8Pz6O2Xp_N-S6m-6zU/pub?output=csv"; 
// ^ Contoh link di atas adalah format yang benar. Ganti dengan link Akang sendiri.

let talents = [];
let currentFilter = "all";

function fixLink(url) {
    if (!url || url.trim() === "" || url.trim() === "-") return null;
    let link = url.trim();
    if (link.includes("dropbox.com")) {
        link = link.replace("www.dropbox.com", "dl.dropboxusercontent.com");
        link = link.replace(/\?dl=[01]/, "?raw=1").replace("&dl=0", "&raw=1");
        if (!link.includes("raw=1")) link += (link.includes("?") ? "&" : "?") + "raw=1";
        return link;
    }
    if (link.includes("drive.google.com")) {
        const match = link.match(/[?&]id=([^&]+)/) || link.match(/\/d\/(.*?)\//) || link.match(/\/file\/d\/(.*?)$/);
        if (match) return `https://docs.google.com/uc?export=open&id=${match[1].split(/[?&/]/)[0]}`;
    }
    return link;
}

async function loadData() {
    const grid = document.getElementById("talentGrid");
    try {
        const res = await fetch(CSV_URL);
        if (!res.ok) throw new Error("Gagal akses Google Sheet. Pastikan sudah 'Publish to Web'.");
        
        const text = await res.text();
        const rows = text.split(/\r?\n/).filter(r => r.trim() !== "");
        
        if (rows.length <= 1) throw new Error("Data di Google Sheet kosong.");

        talents = rows.slice(1).map(row => {
            // Split CSV secara manual agar lebih stabil
            const cols = row.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/).map(c => c.replace(/"/g, "").trim());
            
            let samples = [];
            for (let i = 4; i <= 10; i++) {
                let audio = fixLink(cols[i]);
                if (audio) samples.push(audio);
            }

            let rawCat = (cols[3] || "").toLowerCase();
            let gender = "Other";
            if (rawCat.includes("female") || rawCat.includes("wanita")) gender = "Female";
            else if (rawCat.includes("male") || rawCat.includes("pria")) gender = "Male";

            return {
                name: cols[2] || "Unnamed",
                gender: gender,
                displayGender: cols[3] || "Talent",
                samples: samples
            };
        }).filter(t => t.samples.length > 0);

        render();
    } catch (e) {
        console.error(e);
        grid.innerHTML = `
            <div class="loading" style="color: #ff4444;">
                ⚠️ ERROR: ${e.message}<br>
                <small style="color: #94a3b8;">Cek console (F12) untuk detail.</small>
            </div>`;
    }
}

function render() {
    const grid = document.getElementById("talentGrid");
    const search = document.getElementById("searchInput").value.toLowerCase();
    grid.innerHTML = "";

    const filtered = talents.filter(t => {
        const matchFilter = currentFilter === "all" || t.gender === currentFilter;
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

    const players = document.querySelectorAll("audio");
    players.forEach(p => p.addEventListener("play", () => {
        players.forEach(other => { if(other !== p) other.pause(); });
    }));
}

function setFilter(g) {
    currentFilter = g;
    document.querySelectorAll('.tab-btn').forEach(b => {
        const onc = b.getAttribute('onclick');
        b.classList.toggle('active', onc.includes(`'${g}'`));
    });
    render();
}

document.getElementById("searchInput").addEventListener("input", render);
loadData();
