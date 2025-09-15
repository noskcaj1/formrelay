# Variáveis que serão preenchidas pelo arquivo terraform.tfvars
variable "tenancy_ocid" {}
variable "user_ocid" {}
variable "private_key_path" {}
variable "fingerprint" {}
variable "region" {}

# Bloco de dados para buscar os Domínios de Disponibilidade disponíveis na região
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

# --- 1. CONFIGURAÇÃO DA REDE VIRTUAL (VCN) ---
resource "oci_core_vcn" "formrelay_vcn" {
  compartment_id = var.tenancy_ocid
  display_name   = "formrelay-vcn"
  cidr_block     = "10.0.0.0/16"
  
  # CORREÇÃO DEFINITIVA: Habilita o DNS para a VCN, o que é necessário
  # para que as subnets dentro dela possam ter nomes de DNS.
  dns_label      = "formrelayvcn"
}

# --- 2. CONFIGURAÇÃO DO INTERNET GATEWAY ---
resource "oci_core_internet_gateway" "formrelay_igw" {
  compartment_id = var.tenancy_ocid
  vcn_id         = oci_core_vcn.formrelay_vcn.id
  display_name   = "formrelay-igw"
}

# --- 3. CONFIGURAÇÃO DA TABELA DE ROTAS ---
resource "oci_core_route_table" "formrelay_rt" {
  compartment_id = var.tenancy_ocid
  vcn_id         = oci_core_vcn.formrelay_vcn.id
  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.formrelay_igw.id
  }
  display_name = "formrelay-rt"
}

# --- 4. CONFIGURAÇÃO DA SUBNET ---
resource "oci_core_subnet" "formrelay_subnet" {
  compartment_id             = var.tenancy_ocid
  vcn_id                     = oci_core_vcn.formrelay_vcn.id
  cidr_block                 = "10.0.1.0/24"
  display_name               = "formrelay-subnet"
  dns_label                  = "formrelay"
  prohibit_public_ip_on_vnic = false
  route_table_id             = oci_core_route_table.formrelay_rt.id
  security_list_ids          = [oci_core_security_list.formrelay_sl.id]
}

# --- 5. CONFIGURAÇÃO DO "PORTEIRO" (Security List / Firewall) ---
resource "oci_core_security_list" "formrelay_sl" {
  compartment_id = var.tenancy_ocid
  vcn_id         = oci_core_vcn.formrelay_vcn.id
  display_name   = "formrelay-sl"

  # Regra para permitir tráfego de entrada na porta 22 (SSH)
  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 22
      min = 22
    }
  }

  # Regra para permitir tráfego de entrada na porta 80 (HTTP)
  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 80
      min = 80
    }
  }

  # Regra para permitir tráfego de entrada na porta 443 (HTTPS)
  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 443
      min = 443
    }
  }

  # Regra para permitir todo o tráfego de saída
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
}

# --- 6. BUSCANDO A IMAGEM DO UBUNTU "ALWAYS FREE" (VERSÃO x86_64) ---
data "oci_core_images" "ubuntu_image" {
  compartment_id           = var.tenancy_ocid
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "24.04"
  shape                    = "VM.Standard.E2.1.Micro"
}

# --- 7. DESCRIÇÃO DA MÁQUINA VIRTUAL (A VM - VERSÃO MICRO GARANTIDA) ---
resource "oci_core_instance" "formrelay_vm" {
  compartment_id      = var.tenancy_ocid
  display_name        = "formrelay-vm-prod"
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  shape               = "VM.Standard.E2.1.Micro"

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu_image.images[0].id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.formrelay_subnet.id
    assign_public_ip = true
  }

  metadata = {
    ssh_authorized_keys = file("~/.ssh/id_rsa.pub")
  }
}

# --- 8. SAÍDA DE DADOS (OUTPUT) ---
output "vm_public_ip" {
  value = oci_core_instance.formrelay_vm.public_ip
}