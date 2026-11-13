-- MySQL 8.0.16+: DDL comum a ETL e ELT. Não remove tabelas existentes.
-- Membros SK=0 são publicados junto às dimensões pelos pipelines.

-- 1. DIMENSÃO TEMPO (Calendário e Sazonalidade Epidemiológica)
CREATE TABLE IF NOT EXISTS dim_tempo (
    sk_tempo INTEGER PRIMARY KEY,               -- Formato YYYYMMDD (ou 0 para data ausente)
    data_completa DATE,
    ano INTEGER,
    mes INTEGER,
    nome_mes VARCHAR(20),
    trimestre INTEGER,
    semana_epidemiologica INTEGER,
    periodo_sazonal VARCHAR(40)                 -- 'Alta Transmissão (Jan-Mai)' ou 'Baixa Transmissão (Jun-Dez)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;

-- 2. DIMENSÃO LOCALIDADE (Residência do Paciente)
CREATE TABLE IF NOT EXISTS dim_localidade (
    sk_localidade INTEGER PRIMARY KEY,
    cod_uf_ibge INTEGER,
    sigla_uf CHAR(2) NOT NULL,
    nome_estado VARCHAR(50),
    regiao_brasil VARCHAR(20),
    cod_municipio_ibge6 INTEGER,
    cod_regional_saude INTEGER
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;

-- 3. DIMENSÃO UNIDADE NOTIFICADORA (Local de Atendimento / Notificação)
CREATE TABLE IF NOT EXISTS dim_unidade_notificadora (
    sk_unidade INTEGER PRIMARY KEY,
    cod_unidade_cnes INTEGER,
    cod_uf_notificacao INTEGER,
    sigla_uf_notificacao CHAR(2),
    cod_municipio_notificacao INTEGER,
    cod_regional_notificacao INTEGER
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;

-- 4. DIMENSÃO PACIENTE (Perfil Sociodemográfico e Gestacional)
CREATE TABLE IF NOT EXISTS dim_paciente (
    sk_paciente INTEGER PRIMARY KEY,
    sexo CHAR(1),                               -- 'M', 'F', 'I'
    descricao_sexo VARCHAR(20),                 -- 'Masculino', 'Feminino', 'Ignorado'
    idade_anos INTEGER,
    faixa_etaria VARCHAR(30),                   -- '0 a 14 anos', '15 a 29 anos', '30 a 44 anos', '45 a 59 anos', '60 anos ou mais', 'Ignorado'
    raca_cor VARCHAR(30),                       -- 'Branca', 'Preta', 'Amarela', 'Parda', 'Indígena', 'Ignorado'
    status_gestante VARCHAR(40),                -- '1º Trimestre', '2º Trimestre', '3º Trimestre', 'Idade Gestacional Ignorada', 'Não Gestante', 'Não se aplica', 'Ignorado'
    escolaridade VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;

-- 5. DIMENSÃO INVESTIGAÇÃO E DESFECHO EPIDEMIOLÓGICO
CREATE TABLE IF NOT EXISTS dim_investigacao_desfecho (
    sk_desfecho INTEGER PRIMARY KEY,
    classificacao_final VARCHAR(45),            -- 'Confirmado', 'Descartado', 'Inconclusivo / Em Investigação'
    criterio_confirmacao VARCHAR(45),           -- 'Laboratorial', 'Clínico-Epidemiológico', 'Em Investigação', 'Ignorado / Não Preenchido'
    evolucao_caso VARCHAR(45),                  -- 'Cura', 'Óbito pelo agravo', 'Óbito por outras causas', 'Ignorado / Em Acompanhamento'
    tipo_autoctonia VARCHAR(40),                -- 'Autóctone', 'Importado', 'Indeterminado / Ignorado'
    doenca_trabalho VARCHAR(30)                 -- 'Sim', 'Não', 'Ignorado'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;

-- 6. TABELA FATO CENTRAL: FATO_NOTIFICACAO_ZIKA
CREATE TABLE IF NOT EXISTS fato_notificacao_zika (
    sk_notificacao INTEGER PRIMARY KEY,
    fk_tempo_notificacao INTEGER NOT NULL,
    fk_tempo_sintomas INTEGER NOT NULL,
    fk_localidade_residencia INTEGER NOT NULL,
    fk_unidade_notificadora INTEGER NOT NULL,
    fk_paciente INTEGER NOT NULL,
    fk_desfecho INTEGER NOT NULL,
    qt_notificacoes INTEGER DEFAULT 1 NOT NULL,
    fl_confirmado INTEGER DEFAULT 0 NOT NULL,
    fl_descartado INTEGER DEFAULT 0 NOT NULL,
    fl_gestante INTEGER DEFAULT 0 NOT NULL,
    fl_obito_zika INTEGER DEFAULT 0 NOT NULL,
    qt_dias_atraso_notif INTEGER,
    qt_dias_encerramento INTEGER,
    CONSTRAINT fk_zika_notificacao FOREIGN KEY (fk_tempo_notificacao) REFERENCES dim_tempo(sk_tempo),
    CONSTRAINT fk_zika_sintomas FOREIGN KEY (fk_tempo_sintomas) REFERENCES dim_tempo(sk_tempo),
    CONSTRAINT fk_zika_localidade FOREIGN KEY (fk_localidade_residencia) REFERENCES dim_localidade(sk_localidade),
    CONSTRAINT fk_zika_unidade FOREIGN KEY (fk_unidade_notificadora) REFERENCES dim_unidade_notificadora(sk_unidade),
    CONSTRAINT fk_zika_paciente FOREIGN KEY (fk_paciente) REFERENCES dim_paciente(sk_paciente),
    CONSTRAINT fk_zika_desfecho FOREIGN KEY (fk_desfecho) REFERENCES dim_investigacao_desfecho(sk_desfecho),
    CHECK (qt_notificacoes = 1),
    CHECK (fl_confirmado IN (0,1) AND fl_descartado IN (0,1) AND fl_gestante IN (0,1) AND fl_obito_zika IN (0,1)),
    CHECK (qt_dias_atraso_notif BETWEEN 0 AND 365),
    CHECK (qt_dias_encerramento BETWEEN 0 AND 365)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
