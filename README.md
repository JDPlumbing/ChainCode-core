# ChainCode-core

🧬 A modular identity and trust framework built on atomic chaincodes and structured event logging.

## 🧱 Overview
ChainCode-core generates unique, cryptographically secure chaincodes that represent people, objects, credentials, or concepts. Each chaincode is a standalone unit that can be linked, encrypted, masked, or published to a public ledger.

## 🚀 Features
- Unique 32-byte chaincodes
- Visibility tiers: public, masked, private
- RSA + Fernet encryption
- SLM event support with TrustCoin value
- Local-first logging and offline use
- Supabase sync for public ledger
- CLI interface via `main.py`

## 📦 CLI Usage
Run commands from the project root:

```bash
python main.py generate --type email --value you@example.com
python main.py decrypt --file ./ChainCode-local/abc.json --key ./keys/fernet.key
python main.py sync
python main.py sync-links
python main.py list
```

## 🧩 File Structure
```
ChainCode-core/
├── chaincode/         # Generation, linking, QR, sync
├── events/            # Event schema, master form, trust tracking
├── tools/             # CLI utilities, decryptor
├── keys/              # RSA and Fernet keys
├── ChainCode-local/   # Local store of generated .jsons
├── main.py            # Master CLI entrypoint
```

## 🔐 Security Model
- All fields are optional
- Data can be masked, encrypted, or left local
- Supports privacy-first workflows with optional co-signing

## 🛠️ Requirements
- Python 3.10+
- Dependencies: `pip install -r requirements.txt`
- `.env` with `SUPABASE_URL`, `SUPABASE_API_KEY`, `CHAINCODE_ENCRYPTION_KEY`

## 🧠 Learn More
This project is part of the broader TrustLedger + SLM system.
Contact: admin@jdplumbingsoflo.com
License: MIT
