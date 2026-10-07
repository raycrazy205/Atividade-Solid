from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


# ============================================================
# 1. CARRINHO (SRP: só gerencia produtos e total)
# ============================================================
@dataclass
class Produto:
    nome: str
    preco: float


class Carrinho:
    def __init__(self) -> None:
        self._produtos: List[Produto] = []

    def adicionar_produto(self, nome: str, preco: float) -> None:
        self._produtos.append(Produto(nome, preco))

    @property
    def produtos(self) -> List[Produto]:
        return list(self._produtos)

    @property
    def total(self) -> float:
        return sum(p.preco for p in self._produtos)


# ============================================================
# 2. FRETE (OCP + LSP: novo frete = nova classe)
# ============================================================
class Frete(ABC):
    @abstractmethod
    def calcular(self) -> float:
        pass


class FreteSedex(Frete):
    def calcular(self) -> float:
        return 25.0


class FretePac(Frete):
    def calcular(self) -> float:
        return 15.0


class FreteRetirada(Frete):
    def calcular(self) -> float:
        return 0.0


class FretePadrao(Frete):
    """Mantém o comportamento original para frete desconhecido."""

    def calcular(self) -> float:
        return 50.0


# ============================================================
# 3. DESCONTO (OCP + LSP)
# ============================================================
class Desconto(ABC):
    @abstractmethod
    def calcular(self, total: float) -> float:
        pass


class DescontoPercentual(Desconto):
    def __init__(self, percentual: float) -> None:
        self._percentual = percentual

    def calcular(self, total: float) -> float:
        return total * self._percentual


class SemDesconto(Desconto):
    def calcular(self, total: float) -> float:
        return 0


# ============================================================
# 4. PAGAMENTO (OCP + LSP)
# ============================================================
class Pagamento(ABC):
    @abstractmethod
    def pagar(self, valor: float) -> None:
        pass


class PagamentoPix(Pagamento):
    def pagar(self, valor: float) -> None:
        print("Pagamento realizado via PIX")


class PagamentoCartao(Pagamento):
    def pagar(self, valor: float) -> None:
        print("Pagamento realizado via Cartão")


class PagamentoBoleto(Pagamento):
    def pagar(self, valor: float) -> None:
        print("Pagamento realizado via Boleto")


class PagamentoInvalido(Pagamento):
    def pagar(self, valor: float) -> None:
        print("Forma de pagamento inválida")


# ============================================================
# 5. NOTA FISCAL E NOTIFICAÇÃO (ISP + DIP: interfaces pequenas)
# ============================================================
class EmissorNotaFiscal(ABC):
    @abstractmethod
    def emitir(self) -> None:
        pass


class Notificador(ABC):
    @abstractmethod
    def notificar(self) -> None:
        pass


class NotaFiscalSimples(EmissorNotaFiscal):
    def emitir(self) -> None:
        print("Gerando nota fiscal...")


class NotificadorEmail(Notificador):
    def notificar(self) -> None:
        print("Enviando e-mail de confirmação...")


# ============================================================
# 6. APRESENTAÇÃO (SRP: só imprime o resumo)
# ============================================================
class ResumoCompra:
    @staticmethod
    def exibir(carrinho: Carrinho, desconto: float, frete: float,
               valor_final: float) -> None:
        print("Produtos:")
        for p in carrinho.produtos:
            print(p.nome, p.preco)
        print("Total:", carrinho.total)
        print("Desconto:", desconto)
        print("Frete:", frete)
        print("Valor final:", valor_final)


# ============================================================
# 7. CHECKOUT (DIP: depende de abstrações injetadas)
# ============================================================
class Checkout:
    def __init__(self, emissor: EmissorNotaFiscal, notificador: Notificador) -> None:
        self._emissor = emissor
        self._notificador = notificador

    def finalizar(self, carrinho: Carrinho, desconto: Desconto,
                  frete: Frete, pagamento: Pagamento) -> None:
        valor_desconto = desconto.calcular(carrinho.total)
        valor_frete = frete.calcular()
        valor_final = carrinho.total - valor_desconto + valor_frete

        ResumoCompra.exibir(carrinho, valor_desconto, valor_frete, valor_final)

        pagamento.pagar(valor_final)
        self._emissor.emitir()
        self._notificador.notificar()


# ============================================================
# 8. REGISTROS (mantêm a interface externa por strings)
#    Para estender: basta registrar, sem alterar o Checkout.
# ============================================================
FRETES = {
    "sedex": FreteSedex(),
    "pac": FretePac(),
    "retirada": FreteRetirada(),
}

DESCONTOS = {
    "comum": DescontoPercentual(0.05),
    "premium": DescontoPercentual(0.10),
    "vip": DescontoPercentual(0.15),
}

PAGAMENTOS = {
    "pix": PagamentoPix(),
    "cartao": PagamentoCartao(),
    "boleto": PagamentoBoleto(),
}


def finalizar_compra(carrinho: Carrinho, tipo_cliente: str,
                     tipo_frete: str, tipo_pagamento: str) -> None:
    checkout = Checkout(NotaFiscalSimples(), NotificadorEmail())
    checkout.finalizar(
        carrinho,
        DESCONTOS.get(tipo_cliente, SemDesconto()),
        FRETES.get(tipo_frete, FretePadrao()),
        PAGAMENTOS.get(tipo_pagamento, PagamentoInvalido()),
    )


# ============================================================
# EXECUÇÃO
# ============================================================
if __name__ == "__main__":
    carrinho = Carrinho()
    carrinho.adicionar_produto("Notebook", 3500)
    carrinho.adicionar_produto("Mouse", 120)

    finalizar_compra(carrinho, "premium", "sedex", "pix")

    # Extensão sem alterar código existente (demonstração OCP)
    print("\n--- Demonstração de extensão (OCP) ---")

    class PagamentoCarteiraDigital(Pagamento):
        def pagar(self, valor: float) -> None:
            print("Pagamento realizado via Carteira Digital")

    class FreteExpress(Frete):
        def calcular(self) -> float:
            return 40.0

    PAGAMENTOS["carteira"] = PagamentoCarteiraDigital()
    FRETES["express"] = FreteExpress()

    carrinho2 = Carrinho()
    carrinho2.adicionar_produto("Teclado", 200)
    finalizar_compra(carrinho2, "vip", "express", "carteira")