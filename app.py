from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InventoryItem:
    name: str
    quantity: float
    unit: str
    unit_cost: float

    def consume(self, amount: float) -> None:
        if amount > self.quantity:
            raise ValueError(f"Estoque insuficiente de {self.name}")
        self.quantity -= amount


@dataclass
class Recipe:
    name: str
    ingredients: Dict[str, float]  # item -> quantity needed per unit


@dataclass
class Customer:
    name: str
    contact: str = ""


@dataclass
class Sale:
    recipe: Recipe
    quantity: int
    sale_price: float
    ingredient_cost: float
    customer: Optional[Customer] = None

    @property
    def total_revenue(self) -> float:
        return self.sale_price * self.quantity


@dataclass
class Inventory:
    items: Dict[str, InventoryItem] = field(default_factory=dict)

    def add_or_update_item(self, name: str, quantity: float, unit: str, unit_cost: float) -> None:
        name_key = name.lower()
        if name_key in self.items:
            item = self.items[name_key]
            item.quantity += quantity
            item.unit_cost = unit_cost
        else:
            self.items[name_key] = InventoryItem(name=name, quantity=quantity, unit=unit, unit_cost=unit_cost)

    def can_make(self, recipe: Recipe, quantity: int) -> bool:
        for ingredient, amount in recipe.ingredients.items():
            needed = amount * quantity
            item = self.items.get(ingredient.lower())
            if item is None or item.quantity < needed:
                return False
        return True

    def max_producible(self, recipe: Recipe) -> int:
        max_count = float("inf")
        for ingredient, amount in recipe.ingredients.items():
            item = self.items.get(ingredient.lower())
            if item is None or item.quantity <= 0:
                return 0
            max_count = min(max_count, int(item.quantity // amount))
        return int(max_count)

    def consume_for_recipe(self, recipe: Recipe, quantity: int) -> float:
        if not self.can_make(recipe, quantity):
            raise ValueError("Estoque insuficiente para essa receita")

        total_cost = 0.0
        for ingredient, amount in recipe.ingredients.items():
            needed = amount * quantity
            item = self.items[ingredient.lower()]
            item.consume(needed)
            total_cost += needed * item.unit_cost
        return total_cost

    def summary(self) -> str:
        lines = ["Estoque atual:"]
        for item in sorted(self.items.values(), key=lambda x: x.name):
            lines.append(
                f"- {item.name}: {item.quantity:.2f} {item.unit} (custo unitário: R$ {item.unit_cost:.2f})"
            )
        return "\n".join(lines)


class CashRegister:
    def __init__(self, inventory: Inventory):
        self.inventory = inventory
        self.sales: List[Sale] = []
        self.expenses: float = 0.0

    def record_sale(self, recipe: Recipe, quantity: int, sale_price: float, customer: Optional[Customer] = None) -> None:
        ingredient_cost = self.inventory.consume_for_recipe(recipe, quantity)
        sale = Sale(recipe=recipe, quantity=quantity, sale_price=sale_price, ingredient_cost=ingredient_cost, customer=customer)
        self.sales.append(sale)

    def close_day(self, extra_expenses: float = 0.0) -> Dict[str, float]:
        self.expenses += extra_expenses
        revenue = sum(s.total_revenue for s in self.sales)
        ingredient_cost = sum(s.ingredient_cost for s in self.sales)
        gross_profit = revenue - ingredient_cost
        net_profit = gross_profit - self.expenses
        return {
            "receita": revenue,
            "custo_ingredientes": ingredient_cost,
            "lucro_bruto": gross_profit,
            "despesas": self.expenses,
            "lucro_liquido": net_profit,
        }


class App:
    def __init__(self):
        self.inventory = Inventory()
        self.recipes: Dict[str, Recipe] = {}
        self.customers: Dict[str, Customer] = {}
        self.cash_register = CashRegister(self.inventory)
        self._seed_default_recipe()

    def _seed_default_recipe(self):
        sanduiche = Recipe(
            name="Sanduíche de Frango",
            ingredients={
                "frango": 80.0,  # gramas
                "presunto": 1.0,  # fatia
                "queijo": 1.0,  # fatia
                "hamburguer": 1.0,  # unidade
                "ovo": 1.0,  # unidade
                "alface": 1.0,  # folha
                "tomate": 1.0,  # fatia
            },
        )
        self.recipes[sanduiche.name.lower()] = sanduiche

    def add_recipe(self, name: str, ingredients: Dict[str, float]) -> None:
        self.recipes[name.lower()] = Recipe(name=name, ingredients={k.lower(): v for k, v in ingredients.items()})

    def add_customer(self, name: str, contact: str = "") -> None:
        self.customers[name.lower()] = Customer(name=name, contact=contact)

    def get_recipe(self, name: str) -> Recipe:
        recipe = self.recipes.get(name.lower())
        if recipe is None:
            raise ValueError("Receita não encontrada")
        return recipe

    def get_customer(self, name: str) -> Optional[Customer]:
        return self.customers.get(name.lower())

    def menu(self):
        print("\n=== Lanchonete Manager ===")
        while True:
            print(
                "\nEscolha uma opção:\n"
                "1. Cadastrar/atualizar item no estoque\n"
                "2. Cadastrar receita\n"
                "3. Cadastrar cliente\n"
                "4. Registrar venda\n"
                "5. Ver estoque\n"
                "6. Ver quantas unidades posso produzir de uma receita\n"
                "7. Fechar caixa e sair\n"
            )
            choice = input("Opção: ").strip()

            try:
                if choice == "1":
                    self._menu_add_inventory()
                elif choice == "2":
                    self._menu_add_recipe()
                elif choice == "3":
                    self._menu_add_customer()
                elif choice == "4":
                    self._menu_record_sale()
                elif choice == "5":
                    print(self.inventory.summary())
                elif choice == "6":
                    self._menu_max_producible()
                elif choice == "7":
                    self._menu_close_day()
                    break
                else:
                    print("Opção inválida, tente novamente.")
            except ValueError as exc:
                print(f"Erro: {exc}")

    def _menu_add_inventory(self):
        name = input("Nome do item: ").strip()
        quantity = float(input("Quantidade a adicionar: "))
        unit = input("Unidade (g, un, ml, etc): ").strip() or "un"
        unit_cost = float(input("Custo unitário (R$): "))
        self.inventory.add_or_update_item(name, quantity, unit, unit_cost)
        print(f"Item {name} atualizado no estoque.")

    def _menu_add_recipe(self):
        name = input("Nome da receita: ").strip()
        ingredients: Dict[str, float] = {}
        print("Informe ingredientes (deixe o nome vazio para terminar):")
        while True:
            ing_name = input("Ingrediente: ").strip()
            if not ing_name:
                break
            amount = float(input("Quantidade por unidade: "))
            ingredients[ing_name.lower()] = amount
        self.add_recipe(name, ingredients)
        print(f"Receita {name} cadastrada.")

    def _menu_add_customer(self):
        name = input("Nome do cliente: ").strip()
        contact = input("Contato (opcional): ").strip()
        self.add_customer(name, contact)
        print(f"Cliente {name} cadastrado.")

    def _menu_record_sale(self):
        recipe_name = input("Nome da receita vendida: ").strip()
        recipe = self.get_recipe(recipe_name)
        quantity = int(input("Quantidade vendida: "))
        sale_price = float(input("Preço de venda por unidade (R$): "))
        customer_name = input("Cliente (opcional): ").strip()
        customer = self.get_customer(customer_name) if customer_name else None
        self.cash_register.record_sale(recipe, quantity, sale_price, customer)
        print("Venda registrada com sucesso.")

    def _menu_max_producible(self):
        recipe_name = input("Receita: ").strip()
        recipe = self.get_recipe(recipe_name)
        max_units = self.inventory.max_producible(recipe)
        print(f"Com o estoque atual é possível produzir {max_units} unidade(s) de {recipe.name}.")

    def _menu_close_day(self):
        extra_expenses = float(input("Despesas adicionais do dia (R$): "))
        summary = self.cash_register.close_day(extra_expenses)
        print("\n=== Fechamento do Caixa ===")
        print(f"Receita total: R$ {summary['receita']:.2f}")
        print(f"Custo de ingredientes: R$ {summary['custo_ingredientes']:.2f}")
        print(f"Lucro bruto: R$ {summary['lucro_bruto']:.2f}")
        print(f"Despesas: R$ {summary['despesas']:.2f}")
        print(f"Lucro líquido: R$ {summary['lucro_liquido']:.2f}")


def main():
    app = App()
    app.menu()


if __name__ == "__main__":
    main()
