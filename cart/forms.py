from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)] 

class CartAddProductForm(forms.Form):
    # render visible quantity input with choices (1 to 20)
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int,
        widget=forms.NumberInput(attrs={
            'class': 'quantity-product',
            'value': '1', # default quantity
            'name': 'number', # to match the template if JS depends on it
            'min': '1', # Enforcing a minimum value of 0 on the frontend
            'max': '20', # Enforcing a maximum value of 20 on the frontend
        }),
    )
    # Override boolean field (hidden input)
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )
    
    