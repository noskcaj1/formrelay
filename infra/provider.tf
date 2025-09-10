# Bloco de configuração do Terraform
terraform {
  required_providers {
    # Define que vamos usar o provedor "oci" (Oracle Cloud Infrastructure)
    # e especifica uma versão compatível.
    oci = {
      source  = "oracle/oci"
      version = "~> 5.1"
    }
  }
}

# Bloco de configuração do provedor
provider "oci" {
  # O Terraform vai procurar as credenciais de autenticação
  # em um arquivo de configuração padrão no seu computador.
  # Vamos configurar isso no próximo passo.
}