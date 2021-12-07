FROM jupyterhub/jupyterhub:2.0

RUN /bin/bash -c "\
      sed -i 's/DIR_MODE=0755/DIR_MODE=0750/g' /etc/adduser.conf && \
      adduser jupyterhub --disabled-password --gecos '' --shell /bin/bash && \
      usermod -aG sudo jupyterhub \
    "

WORKDIR /home/jupyterhub/

RUN /bin/bash -c "\
        apt-get update && \
        apt-get install acl sudo git curl nano dirmngr gnupg apt-transport-https ca-certificates software-properties-common texlive-xetex texlive-fonts-recommended texlive-plain-generic pandoc -y \
    "

RUN /bin/bash -c " \
        echo TODO: Upgrade to Python 3.10 && \
        ln -s /usr/bin/python3 /usr/bin/python && \
        exit 0 && \
        apt-get remove python3 python3-pip -y && \
        add-apt-repository ppa:deadsnakes/ppa -y && \
        apt-get install python3.10-distutils -y && \
        apt-get install python3.10 python3-pip -y && \
        rm /usr/bin/python3 && \
        ln -s /usr/bin/python3.10 /usr/bin/python3 && \
        ln -s /usr/bin/python3.10 /usr/bin/python \
    "

RUN /bin/bash -c "\
        python3 -m pip install --upgrade notebook jupyterhub jupyterlab jupyterlab-git oauthenticator jupyterlab-link-share jupyterhub-idle-culler && \
        python3 -m pip install --upgrade tqdm matplotlib scipy numpy flask requests colorama pandas pillow django rsa \
    "

RUN /bin/bash -c "\
        apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9 && \
        add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/' && \
        apt-get install r-base -y && \
        R -e \"install.packages('IRkernel');IRkernel::installspec(user = FALSE);\" \
    "

RUN /bin/bash -c " \
        apt-get remove nodejs npm -y && \
        curl -fsSL https://deb.nodesource.com/setup_current.x | bash - && \
        apt-get install nodejs -y && \
        jupyter labextension install @jupyterlab/hub-extension \
    "

RUN /bin/bash -c " \
        apt-get install julia -y \
    "


RUN /bin/bash -c " \
    touch .flag && \
    exit 0 && \
    mkdir -p /home/jupyterhub/etc/ && \
    mv /etc/passwd /home/jupyterhub/etc/passwd && \
    mv /etc/shadow /home/jupyterhub/etc/shadow && \
    ln -s /home/jupyterhub/etc/passwd /etc/passwd && \
    ln -s /home/jupyterhub/etc/shadow /etc/shadow \
"

COPY jupyterhub_config.py .
COPY admin.py .

ENV JUPYTER_ENABLE_LAB=yes
ENV JUPYTERHUB_SINGLEUSER_APP="notebook.notebookapp.NotebookApp"

VOLUME /home
VOLUME /etc

CMD /usr/local/bin/jupyterhub -f /home/jupyterhub/jupyterhub_config.py