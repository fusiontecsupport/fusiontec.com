from django.db import models

# Contact submission - Enquiry form model

class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.submitted_at.strftime('%Y-%m-%d %H:%M')})"
    

# -----------------------------------------------------------
# Tally full section database models

from django.db import models

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

    def save(self, *args, **kwargs):
        basic = self.basic_amount or 0
        self.total_price = basic + self.cgst + self.sgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tally_1.tally_name} - {self.type_name}"

from django.db import models

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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PI - {self.customer_name} - {self.product_name} ({self.created_at.strftime('%Y-%m-%d')})"

# -----------------------------------------------------------
# E-mudhra section database models
class Emudhra_2(models.Model):
    emudhra_name = models.CharField(max_length=255)
    emudhra_description = models.TextField(blank=True, null=True)
    emudhra_image = models.ImageField(upload_to='products/')
    emudhra_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.emudhra_name

class Emudhra_product(models.Model):
    emudhra_2 = models.ForeignKey(Emudhra_2, on_delete=models.CASCADE)  # Use lowercase for field name
    class_product = models.CharField(max_length=255, null=True)
    emudhra_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.class_product} - {self.emudhra_rate}"
    
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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PI Submission: {self.customer_name} - {self.product_name}"
    
# -----------------------------------------------------------
# Fusiontec section database models

class Fusiontec_3(models.Model):
    fusiontec_name = models.CharField(max_length=255)
    fusiontec_description = models.TextField(blank=True, null=True)
    fusiontec_image = models.ImageField(upload_to='products/')
    fusiontec_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.fusiontec_name

class Fusiontec_product(models.Model):
    fusiontec_3 = models.ForeignKey(Fusiontec_3, on_delete=models.CASCADE)  
    fusiontec_product = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.fusiontec_product
    
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
    team_name = models.CharField(max_length=255, default="For Sales Team") 

    def __str__(self):
        return f"{self.team_name} ({self.new_price})"

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
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PI for {self.customer_name} - {self.product_name}"


#Create Razorpay Model
    
# models.py
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
