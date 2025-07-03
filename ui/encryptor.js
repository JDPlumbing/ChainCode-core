// Real AES-GCM Encryptor/Decryptor (client-side only)

let currentJSON = {};
let aesKey;

async function parseJSON() {
  const fileInput = document.getElementById('jsonFileInput');
  const textInput = document.getElementById('jsonInput').value.trim();
  if (fileInput.files.length > 0) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        currentJSON = JSON.parse(e.target.result);
        renderFieldSelector(currentJSON);
      } catch (err) {
        alert('Invalid JSON');
      }
    };
    reader.readAsText(fileInput.files[0]);
  } else if (textInput) {
    try {
      currentJSON = JSON.parse(textInput);
      renderFieldSelector(currentJSON);
    } catch (err) {
      alert('Invalid JSON');
    }
  } else {
    alert('Please upload or paste JSON');
  }
}

function renderFieldSelector(json) {
  const form = document.getElementById('fieldForm');
  form.innerHTML = '';
  const metadata = json.metadata || {};
  Object.keys(metadata).forEach(key => {
    form.innerHTML += `<label><input type="checkbox" name="fields" value="${key}" checked> ${key}: ${metadata[key]}</label><br>`;
  });
  document.getElementById('fieldSelector').style.display = 'block';
}

async function generateKey() {
  return await window.crypto.subtle.generateKey(
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt", "decrypt"]
  );
}

async function exportKey(key) {
  const raw = await window.crypto.subtle.exportKey("raw", key);
  return btoa(String.fromCharCode(...new Uint8Array(raw)));
}

async function encryptFields() {
  const checkboxes = document.querySelectorAll('input[name="fields"]:checked');
  if (!checkboxes.length) return alert('Select at least one field');

  aesKey = await generateKey();
  const exportedKey = await exportKey(aesKey);
  alert("🔐 Encryption Key (save this!):\n" + exportedKey);

  const encrypted = {};
  for (let cb of checkboxes) {
    const field = cb.value;
    const plain = new TextEncoder().encode(currentJSON.metadata[field]);
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const ciphertext = await window.crypto.subtle.encrypt(
      { name: "AES-GCM", iv },
      aesKey,
      plain
    );
    encrypted[field] = {
      iv: btoa(String.fromCharCode(...iv)),
      value: btoa(String.fromCharCode(...new Uint8Array(ciphertext)))
    };
    delete currentJSON.metadata[field];
  }

  currentJSON.encrypted = {
    method: "aes-gcm",
    data: encrypted
  };

  const blob = new Blob([JSON.stringify(currentJSON, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${currentJSON.public_slug || 'chaincode'}.encrypted.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  // Create and download the key file
  const keyBlob = new Blob([`aes-gcm:${exportedKey}`], { type: 'text/plain' });
  const keyUrl = URL.createObjectURL(keyBlob);
  const k = document.createElement('a');
  k.href = keyUrl;
  k.download = `${currentJSON.public_slug || 'chaincode'}.key.txt`;
  document.body.appendChild(k);
  k.click();
  document.body.removeChild(k);
}

async function importKey(base64Key) {
  const raw = Uint8Array.from(atob(base64Key), c => c.charCodeAt(0));
  return await window.crypto.subtle.importKey(
    "raw",
    raw,
    { name: "AES-GCM" },
    true,
    ["encrypt", "decrypt"]
  );
}

function base64ToBytes(str) {
  return Uint8Array.from(atob(str), c => c.charCodeAt(0));
}

async function decryptChaincode() {
  const fileInput = document.getElementById('decryptFileInput');
  const key = document.getElementById('decryptKey').value.trim();
  if (!fileInput.files.length || !key) return alert('Provide file and key');

  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const json = JSON.parse(e.target.result);
      if (!json.encrypted || !json.encrypted.data) return alert('No encrypted fields');
      const importedKey = await importKey(key);
      const output = {};

      for (let [field, { iv, value }] of Object.entries(json.encrypted.data)) {
        const decrypted = await window.crypto.subtle.decrypt(
          { name: "AES-GCM", iv: base64ToBytes(iv) },
          importedKey,
          base64ToBytes(value)
        );
        output[field] = new TextDecoder().decode(decrypted);
      }

      document.getElementById('decryptedOutput').innerText = JSON.stringify(output, null, 2);
    } catch (err) {
      alert('Decryption failed: ' + err.message);
    }
  };
  reader.readAsText(fileInput.files[0]);
}
