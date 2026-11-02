-- ============================================================================
-- UNIVERSIDADE FEDERAL DE PERNAMBUCO (UFPE) - CENTRO DE INFORMÁTICA (CIn)
-- Disciplina: Banco de Dados | Projeto de Integração (2024-2026)
-- Script: 01_create_star_schema.sql
-- Descrição: Criação do Esquema Estrela (Star Schema) para integração das bases
--            ZIKABR24 (2024), CHIKBR25 (2025) e Plataforma Brasil (2026).
-- ============================================================================

DROP TABLE IF EXISTS fato_vigilancia_e_pesquisa;
DROP TABLE IF EXISTS dim_pesquisa_cep;
DROP TABLE IF EXISTS dim_paciente;
DROP TABLE IF EXISTS dim_agravo_cid;
DROP TABLE IF EXISTS dim_localidade;
DROP TABLE IF EXISTS dim_tempo;

-- 1. DIMENSÃO TEMPO
CREATE TABLE dim_tempo (
    sk_tempo INTEGER PRIMARY KEY,          -- Formato YYYYMMDD (ex: 20240315)
    data_completa DATE NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    nome_mes VARCHAR(20),
    trimestre INTEGER NOT NULL,
    semana_epidemiologica INTEGER
);

-- 2. DIMENSÃO LOCALIDADE
CREATE TABLE dim_localidade (
    sk_localidade INTEGER PRIMARY KEY,
    sigla_uf CHAR(2) NOT NULL,
    cod_uf_ibge INTEGER,
    nome_estado VARCHAR(50),
    regiao_brasil VARCHAR(20),
    cod_municipio_ibge6 INTEGER,
    nome_municipio VARCHAR(120)
);

-- 3. DIMENSÃO AGRAVO / CONDIÇÃO DE SAÚDE (CID-10)
CREATE TABLE dim_agravo_cid (
    sk_agravo_cid INTEGER PRIMARY KEY,
    codigo_cid10 VARCHAR(30) NOT NULL,
    nome_condicao VARCHAR(255) NOT NULL,
    categoria_arbovirose VARCHAR(50),      -- 'Zika Vírus', 'Febre de Chikungunya', 'Pesquisa em Arboviroses', 'Outras Condições'
    fonte_origem VARCHAR(30)               -- 'SINAN_ZIKA_2024', 'SINAN_CHIK_2025', 'PLATAFORMA_BRASIL_2026'
);

-- 4. DIMENSÃO PACIENTE (Perfil Demográfico e Clínico - SINAN)
CREATE TABLE dim_paciente (
    sk_paciente INTEGER PRIMARY KEY,
    sexo CHAR(1),                          -- 'M', 'F', 'I', 'N' (Não Aplicável)
    idade_anos INTEGER,
    faixa_etaria VARCHAR(30),              -- '0-14', '15-29', '30-44', '45-59', '60+', 'Ignorado', 'Não Aplicável'
    raca_cor VARCHAR(30),                  -- 'Branca', 'Preta', 'Amarela', 'Parda', 'Indígena', 'Ignorado', 'Não Aplicável'
    status_gestante VARCHAR(40),           -- 'Gestante (1º ao 3º Trimestre)', 'Não Gestante', 'Ignorado/Não Aplicável'
    evolucao_caso VARCHAR(40)              -- 'Cura', 'Óbito pelo agravo', 'Óbito por outras causas', 'Ignorado/Não Aplicável'
);

-- 5. DIMENSÃO PESQUISA ÉTICA / CEP (Plataforma Brasil)
CREATE TABLE dim_pesquisa_cep (
    sk_pesquisa INTEGER PRIMARY KEY,
    numero_caae VARCHAR(45),
    tipo_estudo VARCHAR(40),
    tipo_centro VARCHAR(40),
    instituicao_proponente VARCHAR(255),
    nome_cep VARCHAR(255),
    situacao_parecer VARCHAR(40)
);

-- 6. TABELA FATO CENTRAL
CREATE TABLE fato_vigilancia_e_pesquisa (
    sk_evento_fato INTEGER PRIMARY KEY,
    fk_tempo INTEGER NOT NULL REFERENCES dim_tempo(sk_tempo),
    fk_localidade INTEGER NOT NULL REFERENCES dim_localidade(sk_localidade),
    fk_agravo_cid INTEGER NOT NULL REFERENCES dim_agravo_cid(sk_agravo_cid),
    fk_perfil_paciente INTEGER NOT NULL REFERENCES dim_paciente(sk_paciente),
    fk_protocolo_pesquisa INTEGER NOT NULL REFERENCES dim_pesquisa_cep(sk_pesquisa),
    qt_notificacao_zika INTEGER DEFAULT 0 NOT NULL,
    qt_notificacao_chik INTEGER DEFAULT 0 NOT NULL,
    qt_caso_confirmado INTEGER DEFAULT 0 NOT NULL,
    qt_hospitalizacao INTEGER DEFAULT 0 NOT NULL,
    qt_dias_atraso_notif INTEGER,
    qt_pesquisa_aprovada INTEGER DEFAULT 0 NOT NULL,
    nu_versao_projeto INTEGER
);

-- ============================================================================
-- INSERÇÃO DE REGISTROS PADRÃO (SK = 0) PARA INTEGRIDADE REFERENCIAL
-- ============================================================================

INSERT INTO dim_paciente (sk_paciente, sexo, idade_anos, faixa_etaria, raca_cor, status_gestante, evolucao_caso)
VALUES (0, 'N', NULL, 'Não Aplicável', 'Não Aplicável', 'Não Aplicável', 'Não Aplicável');

INSERT INTO dim_pesquisa_cep (sk_pesquisa, numero_caae, tipo_estudo, tipo_centro, instituicao_proponente, nome_cep, situacao_parecer)
VALUES (0, 'N/A', 'Não Aplicável', 'Não Aplicável', 'Notificação Epidemiológica SINAN', 'Não Aplicável', 'Não Aplicável');