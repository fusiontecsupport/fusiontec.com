from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

# ============================================================================
# BASE ABSTRACT MODELS
# ============================================================================

class BaseTimestampModel(models.Model):
    """Base model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class BasePricingModel(models.Model):
    """Base model for pricing fields"""
    basic_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Base price without taxes"
    )
    cgst = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Central GST amount"
    )
    sgst = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        help_text="State GST amount"
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        editable=False, 
        default=0,
        help_text="Total price including taxes"
    )
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        # Auto-calculate total price
        basic = self.basic_amount or 0
        self.total_price = basic + self.cgst + self.sgst
        super().save(*args, **kwargs)

class BaseTokenModel(models.Model):
    """Base model for token and installation charges"""
    token_name = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Name of the token/license"
    )
    token_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Token/license cost"
    )
    installing_charges = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Installation charges"
    )
    
    class Meta:
        abstract = True

# ============================================================================
# PRODUCT MASTER (4 Main Products)
# ============================================================================

class ProductMaster(BaseTimestampModel):
    """Main product categories - Tally, E-Mudhra, FusionTec, Business Intelligence"""
    
    PRODUCT_CHOICES = [
        ('tally', 'Tally Software'),
        ('emudhra', 'E-Mudhra'),
        ('fusiontec', 'FusionTec Software'),
        ('biz', 'Business Intelligence'),
    ]
    
    product_code = models.CharField(
        max_length=10, 
        choices=PRODUCT_CHOICES, 
        unique=True,
        help_text="Unique product identifier"
    )
    product_name = models.CharField(
        max_length=255,
        help_text="Display name of the product"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Product description"
    )
    image = models.ImageField(
        upload_to='products/master/', 
        blank=True, 
        null=True,
        help_text="Product logo/image"
    )
    website_link = models.URLField(
        blank=True, 
        null=True,
        help_text="Official product website"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this product is available"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order for display on website"
    )
    
    class Meta:
        ordering = ['display_order', 'product_name']
        verbose_name = "Product Master"
        verbose_name_plural = "Product Masters"
    
    def __str__(self):
        return f"{self.get_product_code_display()} - {self.product_name}"
    
    def get_product_types_count(self):
        """Get count of product types"""
        return self.product_types.count()

# ============================================================================
# PRODUCT TYPES (Sub-categories for each main product)
# ============================================================================

class ProductType(BaseTimestampModel):
    """Product types/categories under each main product"""
    
    product_master = models.ForeignKey(
        ProductMaster, 
        on_delete=models.CASCADE, 
        related_name='product_types',
        help_text="Main product this type belongs to"
    )
    type_code = models.CharField(
        max_length=50,
        help_text="Unique type identifier within the product"
    )
    type_name = models.CharField(
        max_length=255,
        help_text="Name of the product type"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Type description"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this type is available"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order for display"
    )
    
    class Meta:
        ordering = ['product_master', 'display_order', 'type_name']
        unique_together = ['product_master', 'type_code']
        verbose_name = "Product Type"
        verbose_name_plural = "Product Types"
    
    def __str__(self):
        return f"{self.product_master.product_name} - {self.type_name}"
    
    def get_items_count(self):
        """Get count of items under this type"""
        return self.product_items.count()

# ============================================================================
# PRODUCT ITEMS (Services, Upgrades, etc. under each type)
# ============================================================================

class ProductItem(BaseTimestampModel, BasePricingModel, BaseTokenModel):
    """Individual products/services under each product type"""
    
    ITEM_CATEGORIES = [
        ('product', 'Product'),
        ('service', 'Service'),
        ('upgrade', 'Upgrade'),
        ('plan', 'Subscription Plan'),
        ('addon', 'Add-on'),
    ]
    
    product_type = models.ForeignKey(
        ProductType, 
        on_delete=models.CASCADE, 
        related_name='product_items',
        help_text="Product type this item belongs to"
    )
    item_code = models.CharField(
        max_length=50,
        help_text="Unique item identifier within the type"
    )
    item_name = models.CharField(
        max_length=255,
        help_text="Name of the product/service"
    )
    item_category = models.CharField(
        max_length=20,
        choices=ITEM_CATEGORIES,
        default='product',
        help_text="Category of this item"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Item description"
    )
    features = models.TextField(
        blank=True, 
        null=True,
        help_text="Key features of this item"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this item is available"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order for display"
    )
    
    # Special fields for specific product types
    billing_cycle = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        default="Billed for 1 Year | Per Device",
        help_text="Billing frequency and unit"
    )
    old_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Original price before discount"
    )
    team_name = models.CharField(
        max_length=255, 
        default="For Sales Team",
        help_text="Team responsible for this item"
    )
    
    class Meta:
        ordering = ['product_type', 'display_order', 'item_name']
        unique_together = ['product_type', 'item_code']
        verbose_name = "Product Item"
        verbose_name_plural = "Product Items"
    
    def __str__(self):
        return f"{self.product_type.type_name} - {self.item_name}"
    
    def get_discount_percentage(self):
        """Calculate discount percentage if old price exists"""
        if self.old_price and self.basic_amount:
            discount = ((self.old_price - self.basic_amount) / self.old_price) * 100
            return round(discount, 2)
        return 0

# ============================================================================
# RATE CARD MASTER (Pricing history per ProductItem)
# ============================================================================

class RateCardMaster(BaseTimestampModel):
    """Rate cards for a specific product item with effective date and GST%.

    This provides a dedicated table matching the requested structure:
    - References a product (ProductItem)
    - Stores rate/effective date and GST percentage
    - Automatically calculates net amount on save
    """

    product_item = models.ForeignKey(
        ProductItem,
        on_delete=models.CASCADE,
        related_name='rate_cards',
        help_text="Product that this rate card applies to",
    )
    rate_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Optional identifier for this rate card",
    )
    rate_date = models.DateField(help_text="Effective date for this rate")

    base_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Base amount before GST",
    )
    gst_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=18.00,
        help_text="GST percentage to apply (e.g., 18 for 18%)",
    )
    net_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Computed net amount including GST",
    )

    class Meta:
        ordering = ['-rate_date', 'product_item__item_name']
        verbose_name = 'Rate Card'
        verbose_name_plural = 'Rate Cards'
        constraints = [
            models.UniqueConstraint(
                fields=['product_item', 'rate_date'],
                name='unique_rate_per_item_and_date',
            )
        ]

    def __str__(self) -> str:
        return f"{self.product_item.item_name} @ {self.rate_date}"

    def save(self, *args, **kwargs):
        try:
            pct = float(self.gst_percent or 0) / 100.0
        except Exception:
            pct = 0.0
        base_val = float(self.base_amount or 0)
        self.net_amount = base_val * (1 + pct)
        super().save(*args, **kwargs)

# ============================================================================
# CUSTOMER MANAGEMENT
# ============================================================================

class Customer(BaseTimestampModel):
    """Unified customer model"""
    
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, db_index=True)
    mobile = models.CharField(max_length=20, unique=True, db_index=True)
    has_gst = models.BooleanField(default=True)
    gst_number = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    address = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['mobile']),
            models.Index(fields=['gst_number']),
            models.Index(fields=['state', 'district']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.company_name or 'Individual'})"

# ============================================================================
# QUOTE SUBMISSIONS
# ============================================================================

class QuoteSubmission(BaseTimestampModel):
    """Unified quote submission model"""
    
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE,
        related_name='quotes'
    )
    product_item = models.ForeignKey(
        ProductItem, 
        on_delete=models.CASCADE,
        related_name='quote_submissions'
    )
    quantity = models.PositiveIntegerField(default=1)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    installing_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Quote status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Quote #{self.id} - {self.customer.name} - {self.product_item.item_name}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate grand total
        self.grand_total = self.total_amount + self.token_amount + self.installing_charges
        super().save(*args, **kwargs)

# ============================================================================
# CONTACT FORM
# ============================================================================

class ContactSubmission(BaseTimestampModel):
    """Contact form submissions"""
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    
    # Contact status
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

# ============================================================================
# PAYMENT & TRANSACTIONS
# ============================================================================

class PaymentTransaction(BaseTimestampModel):
    """Payment transaction records"""
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quote = models.ForeignKey(QuoteSubmission, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    
    # Razorpay fields
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['razorpay_payment_id']),
        ]
    
    def __str__(self):
        return f"Payment #{self.id} - {self.customer.name} - ₹{self.amount}"

# ============================================================================
# PAYMENT SETTINGS
# ============================================================================

class PaymentSettings(BaseTimestampModel):
    """Payment gateway and method settings"""
    
    SETTING_TYPES = [
        ('razorpay', 'Razorpay'),
        ('qr_code', 'UPI QR Code'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Razorpay specific
    razorpay_key_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_key_secret = models.CharField(max_length=100, blank=True, null=True)
    payment_button_id = models.CharField(max_length=100, blank=True, null=True)
    
    # UPI QR specific
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    qr_image = models.ImageField(upload_to='payment/qr/', blank=True, null=True)
    
    # Bank transfer specific
    account_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=30, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Payment Setting"
        verbose_name_plural = "Payment Settings"
    
    def __str__(self):
        return f"{self.get_setting_type_display()} - {self.title}"

# ============================================================================
# APPLICANT DOCUMENTS
# ============================================================================

class Applicant(BaseTimestampModel):
    """Customer document submissions"""
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='applications')
    reference = models.CharField(max_length=255)
    reference_contact = models.CharField(max_length=15)
    
    # Documents
    pan_copy = models.FileField(upload_to='uploads/pan/', blank=True, null=True)
    aadhar_copy = models.FileField(upload_to='uploads/aadhar/', blank=True, null=True)
    photo = models.ImageField(upload_to='uploads/photo/', blank=True, null=True)
    gst_certificate = models.FileField(upload_to='uploads/gst/', blank=True, null=True)
    authorization_letter = models.FileField(upload_to='uploads/authorization/', blank=True, null=True)
    company_pan = models.FileField(upload_to='uploads/company_pan/', blank=True, null=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Application #{self.id} - {self.customer.name}"

# ============================================================================
# NEW SIMPLE PRODUCT TABLES (Exact table names as requested)
# ============================================================================

class ProductTypeMaster(BaseTimestampModel):
    """Simple lookup for product type.

    DB table name must be exactly 'ProductTypeMaster'. Primary key represents
    PrdtTId. Field `prdt_desc` matches PrdtTDesc from the provided schema.
    """

    prdt_desc = models.CharField(max_length=255, verbose_name="PrdtTDesc")
    image = models.ImageField(upload_to='products/types/', blank=True, null=True, verbose_name="Type Image")

    class Meta:
        db_table = 'ProductTypeMaster'
        verbose_name = 'Product Type Master'
        verbose_name_plural = 'Product Type Master'

    def __str__(self) -> str:
        return self.prdt_desc


class ProductMasterV2(BaseTimestampModel):
    """Minimal product master table linked to `ProductTypeMaster`.

    Table name must be exactly 'ProductMaster'. Primary key represents PrdtId.
    Field `prdt_desc` corresponds to PrdtDesc and `product_type` to PrdtTId.
    """

    product_type = models.ForeignKey(
        ProductTypeMaster,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='PrdtTId',
    )
    prdt_desc = models.CharField(max_length=255, verbose_name='PrdtDesc')

    class Meta:
        db_table = 'ProductMaster'
        verbose_name = 'Product Master (Simple)'
        verbose_name_plural = 'Product Master (Simple)'

    def __str__(self) -> str:
        return self.prdt_desc


class RateCardEntry(BaseTimestampModel):
    """Rate card table linked directly to ProductMasterV2.

    Exact table name 'RateCardMaster'. Fields mirror the provided schema:
    RateCId (pk), PrdtId (FK), RateCDate, BaseAmt, GST%, NettAmt.
    `nett_amt` is auto-computed on save.
    """

    product = models.ForeignKey(
        ProductMasterV2,
        on_delete=models.CASCADE,
        related_name='rate_cards',
        verbose_name='PrdtId',
    )
    rate_date = models.DateField(verbose_name='RateCDate')
    base_amt = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='BaseAmt')
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, verbose_name='GST%')
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='CGST Amount')
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='SGST Amount')
    nett_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name='NettAmt')
    
    # Token and Installation fields
    token_desc = models.CharField(max_length=255, blank=True, null=True, verbose_name='Token Description')
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Token Amount')
    installation_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Installation Charge')
    
    # Token and Installation GST fields
    token_gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, verbose_name='Token GST%')
    token_cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Token CGST')
    token_sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Token SGST')
    token_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name='Token Total')
    
    installation_gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, verbose_name='Installation GST%')
    installation_cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Installation CGST')
    installation_sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Installation SGST')
    installation_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name='Installation Total')
    
    # Total Amount field - sum of base net amount + token total + installation total
    t_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name='Total Amount')

    class Meta:
        db_table = 'RateCardMaster'
        ordering = ['-rate_date', 'product__id']
        verbose_name = 'Rate Card'
        verbose_name_plural = 'Rate Cards'
        constraints = [
            models.UniqueConstraint(fields=['product', 'rate_date'], name='unique_rate_per_product_and_date'),
        ]

    def save(self, *args, **kwargs):
        try:
            pct = float(self.gst_percent or 0) / 100.0
        except Exception:
            pct = 0.0
        base_val = float(self.base_amt or 0)
        # Calculate CGST and SGST as half of total GST for base amount
        total_gst = base_val * pct
        self.cgst = total_gst / 2
        self.sgst = total_gst / 2
        self.nett_amt = base_val + total_gst
        
        # Calculate token GST
        try:
            token_pct = float(self.token_gst_percent or 0) / 100.0
        except Exception:
            token_pct = 0.0
        token_val = float(self.token_amount or 0)
        token_total_gst = token_val * token_pct
        self.token_cgst = token_total_gst / 2
        self.token_sgst = token_total_gst / 2
        self.token_total = token_val + token_total_gst
        
        # Calculate installation GST
        try:
            install_pct = float(self.installation_gst_percent or 0) / 100.0
        except Exception:
            install_pct = 0.0
        install_val = float(self.installation_charge or 0)
        install_total_gst = install_val * install_pct
        self.installation_cgst = install_total_gst / 2
        self.installation_sgst = install_total_gst / 2
        self.installation_total = install_val + install_total_gst
        
        # Calculate total amount (t_amount) - sum of all components
        self.t_amount = self.nett_amt + self.token_total + self.installation_total
        
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.product.prdt_desc} @ {self.rate_date}"