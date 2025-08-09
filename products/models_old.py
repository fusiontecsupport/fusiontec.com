from django.db import models

# -----------------------------------------------------------
# Tally full section database models

class Tally_1(models.Model):
    tally_name = models.CharField(max_length=255)
    tally_description = models.TextField(blank=True, null=True)
    tally_image = models.ImageField(upload_to='products/', blank=True, null=True)
    tally_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.tally_name

class Tally_Product(models.Model):
    tally_1 = models.ForeignKey(Tally_1, on_delete=models.CASCADE, related_name='products')
    type_name = models.CharField(max_length=255, null=True, blank=True)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    # Token configuration fields
    token_name = models.CharField(max_length=255, null=True, blank=True)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installing_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        basic = self.basic_amount or 0
        self.total_price = basic + self.cgst + self.sgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tally_1.tally_name} - {self.type_name}"

class Tally_Software_Service(models.Model):
    tally_1 = models.ForeignKey(Tally_1, on_delete=models.CASCADE, related_name='services')
    type_name = models.CharField(max_length=255, null=True, blank=True)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    # Token configuration fields
    token_name = models.CharField(max_length=255, null=True, blank=True)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installing_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        basic = self.basic_amount or 0
        self.total_price = basic + self.cgst + self.sgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tally_1.tally_name} - {self.type_name}"

class Tally_Upgrade(models.Model):
    tally_1 = models.ForeignKey(Tally_1, on_delete=models.CASCADE, related_name='upgrades')
    type_name = models.CharField(max_length=255, null=True, blank=True)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    # Token configuration fields
    token_name = models.CharField(max_length=255, null=True, blank=True)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installing_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        basic = self.basic_amount or 0
        self.total_price = basic + self.cgst + self.sgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tally_1.tally_name} - {self.type_name}"

class TallyPriceListSubmission(models.Model):
    customer_name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    has_gst = models.BooleanField(default=True)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    product_name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=50)
    product_type_detail = models.CharField(max_length=100, blank=True, null=True)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # Token and installation charge fields
    token_name = models.CharField(max_length=255, blank=True, null=True)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    installing_charges = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PI - {self.customer_name} - {self.product_name} ({self.created_at.strftime('%Y-%m-%d')})"

# -----------------------------------------------------------
# E-mudhra section database models
class Emudhra_2(models.Model):
    emudhra_name = models.CharField(max_length=255)
    emudhra_description = models.TextField(blank=True, null=True)
    emudhra_image = models.ImageField(upload_to='products/', blank=True, null=True)
    emudhra_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.emudhra_name

class Emudhra_product(models.Model):
    emudhra_2 = models.ForeignKey(Emudhra_2, on_delete=models.CASCADE)  # Use lowercase for field name
    class_product = models.CharField(max_length=255, null=True)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0, blank=True, null=True)
    # Token fields
    token_name = models.CharField(max_length=255, null=True, blank=True)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installing_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        basic = self.basic_amount or 0
        self.total_price = basic + self.cgst + self.sgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.class_product} - {self.basic_amount}"
    
class EmudhraPriceListSubmission(models.Model):
    customer_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    has_gst = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    product_name = models.CharField(max_length=255)
    product_type_detail = models.CharField(max_length=255)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PI Submission: {self.customer_name} - {self.product_name}"
    
# -----------------------------------------------------------
# Fusiontec section database models

class Fusiontec_3(models.Model):
    fusiontec_name = models.CharField(max_length=255)
    fusiontec_description = models.TextField(blank=True, null=True)
    fusiontec_image = models.ImageField(upload_to='products/', blank=True, null=True)
    fusiontec_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.fusiontec_name

class Fusiontec_product(models.Model):
    fusiontec_3 = models.ForeignKey(Fusiontec_3, on_delete=models.CASCADE)  
    fusiontec_product = models.CharField(max_length=255, null=True)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    # Token fields
    token_name = models.CharField(max_length=255, null=True, blank=True)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installing_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        basic = self.basic_amount or 0
        self.total_price = basic + self.cgst + self.sgst
        super().save(*args, **kwargs)

    def __str__(self):
        return self.fusiontec_product

class Fusiontec_Software(models.Model):
    fusiontec_3 = models.ForeignKey(Fusiontec_3, on_delete=models.CASCADE, related_name='software')
    software_name = models.CharField(max_length=255, null=True, blank=True)
    software_description = models.TextField(blank=True, null=True)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    # Token fields
    token_name = models.CharField(max_length=255, null=True, blank=True)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installing_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        basic = self.basic_amount or 0
        self.total_price = basic + self.cgst + self.sgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fusiontec_3.fusiontec_name} - {self.software_name}"

class Fusiontec_Service(models.Model):
    fusiontec_3 = models.ForeignKey(Fusiontec_3, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=255, null=True, blank=True)
    service_description = models.TextField(blank=True, null=True)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    # Token fields
    token_name = models.CharField(max_length=255, null=True, blank=True)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installing_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        basic = self.basic_amount or 0
        self.total_price = basic + self.cgst + self.sgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fusiontec_3.fusiontec_name} - {self.service_name}"
    
class FusiontecPriceListSubmission(models.Model):
    customer_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    has_gst = models.CharField(max_length=10)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    product_name = models.CharField(max_length=100)
    product_type_detail = models.CharField(max_length=100)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name

# -----------------------------------------------------------
# biz section database models

class Biz_4(models.Model):
    biz_name = models.CharField(max_length=255)
    biz_description = models.TextField(blank=True, null=True)
    biz_image = models.ImageField(upload_to='products/',blank=True, null=True)
    biz_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.biz_name
    
class biz_product(models.Model):
    biz_4 = models.ForeignKey(Biz_4, on_delete=models.CASCADE)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    billing_cycle = models.CharField( max_length=255,  blank=True,  null=True,  default="Billed for 1 Year | Per Device")
    new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  
    team_name = models.CharField(max_length=255, default="For Sales Team") 
    # Token fields
    token_name = models.CharField(max_length=255, null=True, blank=True)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installing_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        basic = self.new_price or 0
        self.total_price = basic + self.cgst + self.sgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.team_name} ({self.new_price})"

class Biz_Service(models.Model):
    biz_4 = models.ForeignKey(Biz_4, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=255, null=True, blank=True)
    service_description = models.TextField(blank=True, null=True)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    billing_cycle = models.CharField(max_length=255, blank=True, null=True, default="Billed for 1 Year | Per Device")
    # Token fields
    token_name = models.CharField(max_length=255, null=True, blank=True)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installing_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        basic = self.basic_amount or 0
        self.total_price = basic + self.cgst + self.sgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.biz_4.biz_name} - {self.service_name}"

class Biz_Plan(models.Model):
    biz_4 = models.ForeignKey(Biz_4, on_delete=models.CASCADE, related_name='plans')
    plan_name = models.CharField(max_length=255, null=True, blank=True)
    plan_description = models.TextField(blank=True, null=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    billing_cycle = models.CharField(max_length=255, blank=True, null=True, default="Billed for 1 Year | Per Device")
    # Token fields
    token_name = models.CharField(max_length=255, null=True, blank=True)
    token_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installing_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        basic = self.new_price or 0
        self.total_price = basic + self.cgst + self.sgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.biz_4.biz_name} - {self.plan_name}"

class BizPriceListSubmission(models.Model):
    customer_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    has_gst = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')])
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True) 
    pincode = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    product_name = models.CharField(max_length=255)
    business_plan_id = models.IntegerField()  # store the ID of selected business plan
    business_plan_name = models.CharField(max_length=255)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PI for {self.customer_name} - {self.product_name}"

#--------------------------------------------------------------------------------------
#Create Razorpay Model
    
class RazorpayTransactionForm(models.Model):
    customer_name = models.CharField(max_length=100)
    amount = models.FloatField()
    product_name = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100)
    razorpay_order_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.status}"

#---------------------------------------------------------------------------
# netbanking section for QR editing section
class CompanyPaymentInfoQR(models.Model):
    company_name = models.CharField(max_length=100, default="FUSIONTEC SOFTWARE")
    upi_id = models.CharField(max_length=100)
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return self.company_name
    
#---------------------------------------------------------------------------
# netbanking section bank details

class BankTransferInfo(models.Model):
    title = models.CharField(max_length=100, default="Bank Transfer")
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)

    def __str__(self):
        return self.account_name
    
#---------------------------------------------------------------------------
# netbanking section razor pay button

class RazorpayInfo(models.Model):
    title = models.CharField(max_length=100, default="Online Payment (Razorpay)")
    description = models.TextField(default="Secure payment via Razorpay.")
    payment_button_id = models.CharField(max_length=100, help_text="Paste Razorpay payment_button_id here")

    def __str__(self):
        return self.title
    


