-- ============================================================================
-- UNIVERSIDADE FEDERAL DE PERNAMBUCO (UFPE) - CENTRO DE INFORMÁTICA (CIn)
-- Disciplina: Banco de Dados | Projeto de Integração (Triênio 2024-2026)
-- Script: 01_create_star_schema.sql
-- Descrição: Criação do Esquema Estrela (Star Schema) para integração das 3
--            bases anuais de Zika Vírus do SINAN (ZIKABR24, ZIKABR25, ZIKABR26).
-- ============================================================================

DROP TABLE IF EXISTS fato_notificacao_zika;
DROP TABLE IF EXISTS dim_investigacao_desfecho;
DROP TABLE IF EXISTS dim_paciente;
DROP TABLE IF EXISTS dim_unidade_notificadora;
DROP TABLE IF EXISTS dim_localidade;
DROP TABLE IF EXISTS dim_tempo;

-- 1. DIMENSÃO TEMPO (Calendário e Sazonalidade Epidemiológica)
CREATE TABLE dim_tempo (
    sk_tempo INTEGER PRIMARY KEY,               -- Formato YYYYMMDD (ou 0 para data ausente)
    data_completa DATE,
    ano INTEGER,
    mes INTEGER,
    nome_mes VARCHAR(20),
    trimestre INTEGER,
    semana_epidemiologica INTEGER,
    periodo_sazonal VARCHAR(40)                 -- 'Alta Transmissão (Jan-Mai)' ou 'Baixa Transmissão (Jun-Dez)'
);

-- 2. DIMENSÃO LOCALIDADE (Residência do Paciente)
CREATE TABLE dim_localidade (
    sk_localidade INTEGER PRIMARY KEY,
    cod_uf_ibge INTEGER,
    sigla_uf CHAR(2) NOT NULL,
    nome_estado VARCHAR(50),
    regiao_brasil VARCHAR(20),
    cod_municipio_ibge6 INTEGER,
    cod_regional_saude INTEGER
);

-- 3. DIMENSÃO UNIDADE NOTIFICADORA (Local de Atendimento / Notificação)
CREATE TABLE dim_unidade_notificadora (
    sk_unidade INTEGER PRIMARY KEY,
    cod_unidade_cnes INTEGER,
    cod_uf_notificacao INTEGER,
    sigla_uf_notificacao CHAR(2),
    cod_municipio_notificacao INTEGER,
    cod_regional_notificacao INTEGER
);

-- 4. DIMENSÃO PACIENTE (Perfil Sociodemográfico e Gestacional)
CREATE TABLE dim_paciente (
    sk_paciente INTEGER PRIMARY KEY,
    sexo CHAR(1),                               -- 'M', 'F', 'I'
    descricao_sexo VARCHAR(20),                 -- 'Masculino', 'Feminino', 'Ignorado'
    idade_anos INTEGER,
    faixa_etaria VARCHAR(30),                   -- '0 a 14 anos', '15 a 29 anos', '30 a 44 anos', '45 a 59 anos', '60 anos ou mais', 'Ignorado'
    raca_cor VARCHAR(30),                       -- 'Branca', 'Preta', 'Amarela', 'Parda', 'Indígena', 'Ignorado'
    status_gestante VARCHAR(40),                -- '1º Trimestre', '2º Trimestre', '3º Trimestre', 'Idade Gestacional Ignorada', 'Não Gestante', 'Não se aplica', 'Ignorado'
    escolaridade VARCHAR(50)
);

-- 5. DIMENSÃO INVESTIGAÇÃO E DESFECHO EPIDEMIOLÓGICO
CREATE TABLE dim_investigacao_desfecho (
    sk_desfecho INTEGER PRIMARY KEY,
    classificacao_final VARCHAR(45),            -- 'Confirmado', 'Descartado', 'Inconclusivo / Em Investigação'
    criterio_confirmacao VARCHAR(45),           -- 'Laboratorial', 'Clínico-Epidemiológico', 'Em Investigação', 'Ignorado / Não Preenchido'
    evolucao_caso VARCHAR(45),                  -- 'Cura', 'Óbito pelo agravo', 'Óbito por outras causas', 'Ignorado / Em Acompanhamento'
    tipo_autoctonia VARCHAR(40),                -- 'Autóctone', 'Importado', 'Indeterminado / Ignorado'
    doenca_trabalho VARCHAR(30)                 -- 'Sim', 'Não', 'Ignorado'
);

-- 6. TABELA FATO CENTRAL: FATO_NOTIFICACAO_ZIKA
CREATE TABLE fato_notificacao_zika (
    sk_notificacao INTEGER PRIMARY KEY,
    fk_tempo_notificacao INTEGER NOT NULL REFERENCES dim_tempo(sk_tempo),
    fk_tempo_sintomas INTEGER NOT NULL REFERENCES dim_tempo(sk_tempo),
    fk_localidade_residencia INTEGER NOT NULL REFERENCES dim_localidade(sk_localidade),
    fk_unidade_notificadora INTEGER NOT NULL REFERENCES dim_unidade_notificadora(sk_unidade),
    fk_paciente INTEGER NOT NULL REFERENCES dim_paciente(sk_paciente),
    fk_desfecho INTEGER NOT NULL REFERENCES dim_investigacao_desfecho(sk_desfecho),
    qt_notificacoes INTEGER DEFAULT 1 NOT NULL,
    fl_confirmado INTEGER DEFAULT 0 NOT NULL,
    fl_descartado INTEGER DEFAULT 0 NOT NULL,
    fl_gestante INTEGER DEFAULT 0 NOT NULL,
    fl_obito_zika INTEGER DEFAULT 0 NOT NULL,
    qt_dias_atraso_notif INTEGER,
    qt_dias_encerramento INTEGER
);

-- ============================================================================
-- REGISTROS DIMENSIONAIS PADRÃO (SK = 0) PARA TRATAMENTO DE NULOS
-- ============================================================================

INSERT INTO dim_tempo (sk_tempo, data_completa, ano, mes, nome_mes, trimestre, semana_epidemiologica, periodo_sazonal)
VALUES (0, NULL, NULL, NULL, 'Não Informado', NULL, NULL, 'Não Informado');

INSERT INTO dim_localidade (sk_localidade, cod_uf_ibge, sigla_uf, nome_estado, regiao_brasil, cod_municipio_ibge6, cod_regional_saude)
VALUES (0, NULL, 'NI', 'Não Informado', 'Não Informado', NULL, NULL);

INSERT INTO dim_unidade_notificadora (sk_unidade, cod_unidade_cnes, cod_uf_notificacao, sigla_uf_notificacao, cod_municipio_notificacao, cod_regional_notificacao)
VALUES (0, NULL, NULL, 'NI', NULL, NULL);