from django import forms
from django.contrib.auth.models import User

from .models import Aparelho, OrdemServico, RegistroManutencao


class AparelhoForm(forms.ModelForm):
    class Meta:
        model = Aparelho
        fields = "__all__"
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "marca": forms.TextInput(attrs={"class": "form-control"}),
            "modelo": forms.TextInput(attrs={"class": "form-control"}),
            "numero_serie": forms.TextInput(attrs={"class": "form-control"}),
            "cliente": forms.TextInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
        }


class OrdemServicoForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = ["problema_relatado", "prioridade"]
        widgets = {
            "problema_relatado": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "prioridade": forms.Select(attrs={"class": "form-select"}),
        }


class RegistroManutencaoForm(forms.ModelForm):
    class Meta:
        model = RegistroManutencao
        fields = ["tipo_servico", "descricao", "peca_trocada", "foto_1", "foto_2", "foto_3"]
        widgets = {
            "tipo_servico": forms.Select(attrs={"class": "form-select"}),
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "peca_trocada": forms.TextInput(attrs={"class": "form-control"}),
            "foto_1": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "foto_2": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "foto_3": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class CadastroUsuarioForm(forms.ModelForm):
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Senha",
    )
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirmar senha",
    )
    cargo = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Cargo",
    )
    telefone = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Telefone",
        required=False,
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("senha") != cleaned.get("confirmar_senha"):
            raise forms.ValidationError("As senhas não coincidem!")
        return cleaned
