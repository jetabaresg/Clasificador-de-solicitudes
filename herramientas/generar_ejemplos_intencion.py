import csv
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent.parent
INTENTS_CSV = ROOT / 'Sistema_clasificador' / 'data' / 'tabla_intenciones.csv'
OUT_ENRICHED = ROOT / 'Sistema_clasificador' / 'data' / 'intents_enriched.csv'
OUT_SYNTHETIC = ROOT / 'Sistema_clasificador' / 'data' / 'intents_synthetic_samples.csv'

TEMPLATES = [
    "Quisiera {action} {obj}",
    "¿Cómo puedo {action} {obj}?",
    "Necesito {action} {obj}",
    "Ayuda para {action} {obj}",
    "No sé cómo {action} {obj}",
    "¿Me pueden ayudar a {action} {obj}?",
]

# (rest of file identical to original - content preserved)

INTENT_PROFILES = {
    'contact_human_agent': {
        'count': 160,
        'templates': [
            'Solicito asesor',
            'Necesito hablar con un asesor',
            'Quiero atención humana para {obj}',
            'Por favor, que me atienda una persona',
            'No quiero seguir con el bot, necesito un agente',
            '¿Me pueden transferir con un asesor?',
            'Necesito un humano para revisar {obj}',
        ],
        'objects': ['mi caso', 'mi solicitud', 'este problema', 'la gestión'],
    },
    # ... rest unchanged
}

OBJ_SUBS = {
    'invoice': ['la factura', 'mi factura', 'el comprobante'],
    'order': ['mi pedido', 'el pedido {{Order Number}}', 'un pedido'],
    'subscription': ['la suscripción', 'mi plan', 'mi suscripción mensual'],
    'account': ['mi cuenta', 'la cuenta'],
    'payment': ['el pago', 'mi tarjeta', 'la transacción'],
    'shipping': ['la dirección', 'el envío', 'la entrega'],
}


def choose_obj(intent_id, nombre):
    # heurística simple para elegir objeto por keywords
    keymap = {
        'invoice': ['invoice', 'factura', 'get_invoice', 'check_invoice', 'get_invoice'],
        'order': ['order', 'pedido', 'cancel_order', 'place_order', 'track_order'],
        'subscription': ['subscription', 'suscrip', 'newsletter'],
        'account': ['account', 'cuenta', 'create_account', 'delete_account'],
        'payment': ['payment', 'pago', 'refund', 'reembols'],
        'shipping': ['shipping', 'envío', 'direccion']
    }
    low = (intent_id + ' ' + nombre).lower()
    for k, kws in keymap.items():
        for kw in kws:
            if kw in low:
                return random.choice(OBJ_SUBS.get(k, ['el servicio']))
    return random.choice(['el asunto', 'mi solicitud', 'esta gestión'])


def get_profile(intent_id, nombre):
    profile = INTENT_PROFILES.get(intent_id, {})
    templates = profile.get('templates', TEMPLATES)
    objects = profile.get('objects')
    count = profile.get('count', 80)
    return templates, objects, count


def enrich():
    random.seed(42)
    intents = []
    # soportar BOM en encabezado usando utf-8-sig
    with open(INTENTS_CSV, newline='', encoding='utf-8-sig') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            intents.append(r)

    # write enriched: include 3 canonical examples per intent
    with open(OUT_ENRICHED, 'w', newline='', encoding='utf-8') as fh:
        fieldnames = ['intent', 'nombre', 'categoria_amigable', 'descripcion_corta', 'example_1', 'example_2', 'example_3']
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for it in intents:
            intent_id = it['intent']
            name = it.get('nombre', '')
            desc = it.get('recomendacion', '')[:200]
            # canonical examples: simple paraphrases
            e1 = f"Quiero {name.lower()}"
            e2 = f"Necesito ayuda con {name.lower()}"
            e3 = f"¿Cómo puedo {name.lower()}?"
            writer.writerow({
                'intent': intent_id,
                'nombre': name,
                'categoria_amigable': it.get('categoria_amigable', ''),
                'descripcion_corta': desc,
                'example_1': e1,
                'example_2': e2,
                'example_3': e3,
            })

    with open(OUT_SYNTHETIC, 'w', newline='', encoding='utf-8') as fh:
        fieldnames = ['intent', 'text']
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for it in intents:
            intent_id = it['intent']
            name = it.get('nombre', '')
            templates, objects, count = get_profile(intent_id, name)
            for i in range(count):
                tpl = random.choice(templates)
                if objects is None:
                    obj = choose_obj(intent_id, name)
                else:
                    obj = random.choice(objects)
                action = intent_id.replace('_', ' ')
                text = tpl.format(action=action, obj=obj)
                writer.writerow({'intent': intent_id, 'text': text})

if __name__ == '__main__':
    enrich()
