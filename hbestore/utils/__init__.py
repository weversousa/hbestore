from PIL import Image


def formatar_moeda_real(valor):
    if '.' in str(valor):
        reais, centavos = str(valor).split('.')
    else:
        reais, centavos = str(valor), '00'

    reais = list(reais)[::-1]
    real = ''
    r = []
    c = 1
    for n in reais.copy():
        if c == 4:
            r.append('.')
            c = 1
        r.append(n)
        c += 1
        del reais[0]
    r = r[::-1]
    real += ''.join(r) + ',' + centavos
    return real


def calcular_estoque(session, produto_id, estoque):
    if 'cart' in session:
        if str(produto_id) in session['cart']:
            return estoque - session['cart'][str(produto_id)]
    return estoque



def format_image(image_path):
    img = Image.open(image_path)
    img = img.resize((1200, 1200))
    img.save(image_path)
