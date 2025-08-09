# 🚀 FusionTec Database Restructuring Setup Guide

## 📋 **Overview**
This guide will help you migrate from your current database structure to the new, organized hierarchical structure.

## 🏗️ **New Database Structure**

### **1. Product Master (4 Main Categories)**
- **Tally Software** - Accounting and business management
- **E-Mudhra** - Digital signature solutions  
- **FusionTec Software** - Custom software solutions
- **Business Intelligence** - BI and analytics solutions

### **2. Product Types (Sub-categories)**
Each main product has multiple types:
- **Tally**: Main Products, Services, Upgrades
- **E-Mudhra**: Main Products
- **FusionTec**: Main Products, Software, Services
- **Business Intelligence**: Main Products, Services, Subscription Plans

### **3. Product Items (Individual Products/Services)**
Under each type, you have individual items with:
- Pricing (Basic, CGST, SGST, Total)
- Token/License costs
- Installation charges
- Features and descriptions
- Billing cycles and team assignments

## 🔄 **Migration Steps**

### **Step 1: Backup Your Current Database**
```bash
# Create a backup of your current database
mysqldump -u root -p fusion_db > fusion_db_backup_$(date +%Y%m%d_%H%M%S).sql
```

### **Step 2: Update Your Models**
1. **Rename your current models.py to models_old.py**
   ```bash
   mv products/models.py products/models_old.py
   ```

2. **Rename the new models file**
   ```bash
   mv products/models_new.py products/models.py
   ```

3. **Update your admin.py**
   ```bash
   mv products/admin.py products/admin_old.py
   mv products/admin_new.py products/admin.py
   ```

### **Step 3: Create New Migrations**
```bash
# Create new migration files
python manage.py makemigrations

# Apply the migrations
python manage.py migrate
```

### **Step 4: Run Data Migration**
```bash
# Run the data migration script
python manage.py migrate --fake-initial
python manage.py migrate
```

### **Step 5: Verify Data Migration**
1. Check Django admin panel
2. Verify all products are properly categorized
3. Check that pricing and relationships are correct

## 📊 **Database Schema Details**

### **ProductMaster Table**
```sql
CREATE TABLE products_productmaster (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(10) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    image VARCHAR(100),
    website_link VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### **ProductType Table**
```sql
CREATE TABLE products_producttype (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_master_id INT NOT NULL,
    type_code VARCHAR(50) NOT NULL,
    type_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_master_id) REFERENCES products_productmaster(id),
    UNIQUE KEY unique_product_type (product_master_id, type_code)
);
```

### **ProductItem Table**
```sql
CREATE TABLE products_productitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_type_id INT NOT NULL,
    item_code VARCHAR(50) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    item_category VARCHAR(20) DEFAULT 'product',
    description TEXT,
    features TEXT,
    basic_amount DECIMAL(10,2),
    cgst DECIMAL(10,2) DEFAULT 0,
    sgst DECIMAL(10,2) DEFAULT 0,
    total_price DECIMAL(10,2) DEFAULT 0,
    token_name VARCHAR(255),
    token_amount DECIMAL(10,2),
    installing_charges DECIMAL(10,2),
    billing_cycle VARCHAR(255) DEFAULT 'Billed for 1 Year | Per Device',
    old_price DECIMAL(10,2),
    team_name VARCHAR(255) DEFAULT 'For Sales Team',
    is_active BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_type_id) REFERENCES products_producttype(id),
    UNIQUE KEY unique_type_item (product_type_id, item_code)
);
```

## 🎯 **Benefits of New Structure**

### **1. Better Organization**
- Clear hierarchy: Product → Type → Item
- Easy to manage and maintain
- Logical grouping of related products

### **2. Improved Scalability**
- Easy to add new product categories
- Simple to add new types under existing products
- Flexible item categorization

### **3. Enhanced Admin Experience**
- Organized admin interface
- Better filtering and search capabilities
- Improved data visualization

### **4. Better Data Integrity**
- Proper foreign key relationships
- Consistent data structure
- Reduced data duplication

## 🔧 **Post-Migration Tasks**

### **1. Update Your Views**
Update your views to use the new model structure:
```python
# Old way
tally_products = Tally_Product.objects.all()

# New way
tally_products = ProductItem.objects.filter(
    product_type__product_master__product_code='tally'
)
```

### **2. Update Your Templates**
Update templates to use new model fields:
```html
<!-- Old way -->
{{ product.type_name }}

<!-- New way -->
{{ product.item_name }}
```

### **3. Update Your Forms**
Update forms to work with new models:
```python
# Old way
class TallyProductForm(forms.ModelForm):
    class Meta:
        model = Tally_Product
        fields = ['type_name', 'basic_amount', ...]

# New way
class ProductItemForm(forms.ModelForm):
    class Meta:
        model = ProductItem
        fields = ['item_name', 'basic_amount', ...]
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Migration Errors**
   - Check if all old models are properly imported
   - Verify database connection
   - Check for conflicting field names

2. **Data Not Migrating**
   - Verify old model names match exactly
   - Check field mappings in migration script
   - Review error logs

3. **Admin Panel Issues**
   - Clear browser cache
   - Restart Django server
   - Check admin.py imports

### **Rollback Plan**
If something goes wrong:
```bash
# Restore from backup
mysql -u root -p fusion_db < fusion_db_backup_YYYYMMDD_HHMMSS.sql

# Revert model changes
mv products/models_old.py products/models.py
mv products/admin_old.py products/admin.py
```

## 📞 **Support**
If you encounter any issues during migration:
1. Check the Django error logs
2. Verify database permissions
3. Ensure all dependencies are installed
4. Test with a small dataset first

## ✨ **Next Steps**
After successful migration:
1. Test all functionality thoroughly
2. Update any custom scripts or APIs
3. Train your team on the new structure
4. Plan for future enhancements

---

**Good luck with your database restructuring! 🎉**
