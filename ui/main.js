// Updated main.js rendering logic with friendly visuals

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const output = document.querySelector("#output");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    output.innerHTML = "<p>⏳ Generating chaincodes...</p>";

    const formData = new FormData(form);
    const fields = {};
    let entity_type = "entity";
    let register = false;
    let download = false;

    for (const [key, value] of formData.entries()) {
      if (key === "entity_type") entity_type = value;
      else if (key === "register") register = true;
      else if (key === "download") download = true;
      else if (key !== "visibility" && value.trim() !== "") fields[key] = value.trim();
    }

    const payload = {
      entity_type,
      fields,
      register,
      download
    };

    try {
      const res = await fetch("/generate_entity", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      const { entity, fields: fieldResults, links } = data;

      const html = [
        `<div class="result-card">`,
        `<h3>🧬 Chaincode Created</h3>`,
        `<p><strong>Entity Type:</strong> ${entity.metadata.type}</p>`,
        `<p><strong>Slug:</strong> <code>${entity.public_slug}</code> <button data-copy="${entity.public_slug}">📋 Copy</button></p>`,
        `<p><strong>Visibility:</strong> ${entity.metadata.visibility}</p>`,
        `<p><strong>Chaincode ID:</strong> <code>${entity.chaincode_id}</code> <button data-copy="${entity.chaincode_id}">📋 Copy</button></p>`,

        `<h4>📎 Linked Fields:</h4>`,
        `<ul>` + fieldResults.map(f => `<li><strong>${f.metadata.type}:</strong> ${f.metadata.value}</li>`).join("") + `</ul>`,

        `<h4>🔗 Links:</h4>`,
        `<ul>` + links.map(link => `<li><code>${link.from_id.slice(0,12)}</code> → <code>${link.to_id.slice(0,12)}</code> (<em>${link.link_type}</em>)</li>`).join("") + `</ul>`,

        `<details><summary>📄 Raw JSON Output</summary><pre>${JSON.stringify(data, null, 2)}</pre></details>`,
        `</div>`
      ];

      // Add optional download list
      if (download) {
        html.push(`<h4>📥 Downloads:</h4><ul>`);
        html.push(`<li><a href="/download/${entity.public_slug}" target="_blank">Entity: ${entity.public_slug}.json</a></li>`);
        fieldResults.forEach(f => {
          html.push(`<li><a href="/download/${f.public_slug}" target="_blank">${f.metadata.type}: ${f.public_slug}.json</a></li>`);
        });
        html.push(`</ul>`);
      }

      // Copy button logic
      setTimeout(() => {
        document.querySelectorAll('[data-copy]').forEach(btn => {
          btn.addEventListener('click', () => {
            const val = btn.getAttribute('data-copy');
            navigator.clipboard.writeText(val).then(() => {
              btn.innerText = '📋 Copied!';
              setTimeout(() => btn.innerText = '📋 Copy', 1500);
            });
          });
        });
      }, 100);

      output.innerHTML = html.join("");

      if (download && entity.public_slug) {
        const slug = entity.public_slug;
        const downloadUrl = `/download/${slug}`;
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = `${slug}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }
    } catch (err) {
      output.innerHTML = `<p style="color:red;">❌ Error:<br><br>${err.message}</p>`;
    }
  });
});
