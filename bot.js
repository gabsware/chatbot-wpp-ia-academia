const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const client = new Client();

const mensagensProcessadas = new Set();

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✅ WhatsApp conectado!');
});

client.on('message', async msg => {

    if (msg.fromMe) return;
    if (!msg.body) return;
    if (msg.from === 'status@broadcast') return;
    if (msg.type !== 'chat') return;

    if (mensagensProcessadas.has(msg.id._serialized)) return;
    mensagensProcessadas.add(msg.id._serialized);

    try {
        const res = await axios.post('http://127.0.0.1:5000/webhook', {
            from: msg.from,
            message: msg.body
        });

        if (res.data.reply) {
            await msg.reply(res.data.reply);
        }

    } catch (err) {
        console.log("ERRO:", err.message);
    }
});

client.initialize();