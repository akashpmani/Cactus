from django import forms
from django.utils.text import slugify
from .models import Category, Products_Table, Product_Tags, Product_Color, Product_images, Product_item, P_tags


class CategoryForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        required=False, queryset=Category.objects.all(), empty_label='')

    class Meta:
        model = Category
        fields = ['category_name', 'slug', 'is_child', 'parent']
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'is_child': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }
        field_options = {
            'is_child': forms.BooleanField(required=False),
        }


class ProductsTags(forms.ModelForm):
    class Meta:
        model = Product_Tags
        fields = ['tag_name', 'slug']
        widgets = {
            'tag_name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProductsTableForm(forms.ModelForm):

    class Meta:
        model = Products_Table
        fields = ['slug', 'category', 'name', 'bio_name',
                  'description', 'care_instruction', 'image']
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'care_instruction': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# class ProductItemForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['is_active'].required = False
#         self.initial['is_active'] = True

#     class Meta:
#         model = Product_item
#         fields = ['product', 'color', 'size',
#                   'price', 'image', 'quantity', 'is_active']
#         widgets = {
#             'product': forms.Select(attrs={'class': 'form-control'}),
#             'color': forms.Select(attrs={'class': 'form-control'}),
#             'size': forms.Select(choices=Product_item.SIZE_CHOICES, attrs={'class': 'form-control'}),
#             'price': forms.NumberInput(attrs={'class': 'form-control'}),
#             'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
#             'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }
#         field_options = {
#             'is_active': forms.BooleanField(required=False),
#         }
class ProductItemForm(forms.ModelForm):

    class Meta:
        model = Product_item
        fields = ['product', 'size',
              'price', 'quantity', 'is_active']
    widgets = {
        'product': forms.Select(attrs={'class': 'form-control'}),
        'size': forms.Select(choices=Product_item.SIZE_CHOICES, attrs={'class': 'form-control'}),
        'price': forms.NumberInput(attrs={'class': 'form-control'}),

        'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
    field_options = {
        'is_active': forms.BooleanField(required=False),
    }

class ProductTagForm(forms.ModelForm):
    options = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple(attrs={'style': 'width: 50px'}))

    class Meta:
        model = P_tags
        fields = ('options',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['options'].choices = [(tag.id, tag.tag_name) for tag in Product_Tags.objects.all()]

class ProductItemUpdateForm(forms.Form):
    price = forms.IntegerField()
    quantity = forms.IntegerField()
    status = forms.CharField()

