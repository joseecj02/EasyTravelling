# Usa una imagen base de PHP con Apache
FROM php:8.2-apache

ENV LISTEN_PORT=5004

RUN sed -i "s/80/${LISTEN_PORT}/g" /etc/apache2/sites-available/000-default.conf
RUN sed -i "s/80/${LISTEN_PORT}/g" /etc/apache2/ports.conf

EXPOSE 5004

# Instala extensiones necesarias
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) gd \
    && docker-php-ext-install pdo pdo_mysql mysqli

# Instala extensiones necesarias para MongoDB
RUN pecl install mongodb && docker-php-ext-enable mongodb

# Copia el código fuente
COPY . /var/www/html/

