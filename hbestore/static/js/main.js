function limpa_formulário_cep() {
    //Limpa valores do formulário de cep.
    document.getElementById('publicPlace').value=("");
    document.getElementById('district').value=("");
    document.getElementById('location').value=("");
    document.getElementById('state').value=("");
}

function meu_callback(conteudo) {
    if (!("erro" in conteudo)) {
        //Atualiza os campos com os valores.
        const weverton_endereco = conteudo.logradouro + "\n" + conteudo.localidade + " - " + conteudo.bairro + " - " + conteudo.uf
        document.getElementById('publicPlace').value=(conteudo.logradouro);
        document.getElementById('district').value=(conteudo.bairro);
        document.getElementById('location').value=(conteudo.localidade);
        document.getElementById('state').value=(conteudo.uf);
    }
    else {
        //CEP não Encontrado.
        limpa_formulário_cep();
        alert("CEP não encontrado.");
    }
}

function pesquisacep(valor) {
    //Nova variável "cep" somente com dígitos.
    var cep = valor.replace(/\D/g, '');

    //Verifica se campo cep possui valor informado.
    if (cep != "") {

        //Expressão regular para validar o CEP.
        var validacep = /^[0-9]{8}$/;

        //Valida o formato do CEP.
        if(validacep.test(cep)) {

            //Preenche os campos com "..." enquanto consulta webservice.
            document.getElementById('publicPlace').value="...";

            //Cria um elemento javascript.
            var script = document.createElement('script');

            //Sincroniza com o callback.
            script.src = 'https://viacep.com.br/ws/'+ cep + '/json/?callback=meu_callback';

            //Insere script no documento e carrega o conteúdo.
            document.body.appendChild(script);

        } //end if.
        else {
            //cep é inválido.
            limpa_formulário_cep();
            alert("Formato de CEP inválido.");
        }
    } //end if.
    else {
        //cep sem valor, limpa formulário.
        limpa_formulário_cep();
    }
};



// CHECKOUT ADDRESS
const buttonContinuar = document.getElementById("continue");
const listAddress = document.getElementsByName("endereco");
let idAddress = null;

for (let address of listAddress) {
    address.addEventListener("change", () => {
        buttonContinuar.removeAttribute("disabled");
        // idAddress = address.id.replace(/\D/gim, '');
    });
}

// CHECKOUT PAYMENT
const buttonFinish = document.getElementById("finish");
const listPayment = document.getElementsByName("pagamento");
let idPayment = null;

for (let payment of listPayment) {
    payment.addEventListener("change", () => {
        buttonFinish.removeAttribute("disabled");
        if (payment.id === "pag2") {
            document.getElementById("txtNome").value=("");
            document.getElementById("txtNumero").value=("");
            document.getElementById("txtValidade").value=("");
            document.getElementById("txtCodigo").value=("");
            document.getElementById("selParcelas").value=("");
        } else if ((payment.id === "pag1")) {
            document.getElementById("txtTroco").value=("");
        }
    });
}


//
let id = ""
const listGroupClientAll = document.getElementsByClassName("list-group-client");

if (window.location.href.includes("personal-data")) id = "personalData";
else if (window.location.href.includes("contacts")) id = "contacts";
else if (window.location.href.includes("address")) id = "address";
else if (window.location.href.includes("address")) id = "requests";
else if (window.location.href.includes("change-password")) id = "changePassword";

for (lis of listGroupClientAll) {
    if (lis.id == id) lis.classList.add("bg-hb");
    else lis.classList.remove("bg-hb", "text-light");
}



function pegarValorDoSelect(evento) {
    window.location.href = "/" + evento.target.value
}


const ordem = document.querySelector(".ordem");
ordem.addEventListener("change", pegarValorDoSelect);

