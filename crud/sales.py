from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from models.sales import Sale, SaleItem
from models.inventory import Inventory
from schemas.sales import SaleCreate


class SalesCRUD:
    @staticmethod
    def create_sale(db: Session, sale_data: SaleCreate, created_by: UUID):
        total = 0
        sale_items = []
        for item in sale_data.items:
            inventory = (
                db.query(Inventory).filter(Inventory.id == item.inventory_id).first()
            )
            if not inventory:
                raise HTTPException(
                    status_code=404,
                    detail=f"Inventory item {item.inventory_id} not found",
                )
            if inventory.quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {inventory.product_name}",
                )
            inventory.quantity -= item.quantity
            db.add(inventory)
            sale_items.append(
                SaleItem(
                    inventory_id=item.inventory_id,
                    quantity=item.quantity,
                    price=item.price,
                    product_name: inventory.product_name,
                )
            )
            total += item.price * item.quantity

        change_given = (
            sale_data.amount_paid - total if sale_data.amount_paid > total else 0
        )
        outstanding_balance = (
            total - sale_data.amount_paid if sale_data.amount_paid < total else 0
        )

        sale = Sale(
            store_id=sale_data.store_id,
            total_amount=total,
            amount_paid=sale_data.amount_paid,
            change_given=change_given,
            outstanding_balance=outstanding_balance,
            payment_method=sale_data.payment_method,
            created_by=sale_data.staff_id,
            items=sale_items,
        )
        db.add(sale)
        db.commit()
        db.refresh(sale)
        return sale

    def get_all_sales(self, db: Session, store_id: UUID):
        return (
            db.query(Sale)
            .filter(Sale.store_id == store_id, Sale.is_deleted == False)
            .all()
        )

    def delete_sale(self, db: Session, sale_id: UUID, staff_id: UUID):
        sale = (
            db.query(Sale).filter(Sale.id == sale_id, Sale.is_deleted == False).first()
        )
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        sale.is_deleted = True
        sale.deleted_by = staff_id
        db.add(sale)
        db.commit()

    def get_sales_stats(self, db: Session, store_id: UUID):
        sales = (
            db.query(Sale)
            .filter(Sale.store_id == store_id, Sale.is_deleted == False)
            .all()
        )
        total_sales = len(sales)
        revenue_generated = sum(s.total_amount for s in sales)
        avg_sales_value = revenue_generated / total_sales if total_sales else 0
        outstanding = sum(s.outstanding_balance for s in sales)
        return {
            "total_sales": total_sales,
            "revenue_generated": revenue_generated,
            "avg_sales_value": avg_sales_value,
            "outstanding_balance": outstanding,
        }


sales_crud = SalesCRUD()
