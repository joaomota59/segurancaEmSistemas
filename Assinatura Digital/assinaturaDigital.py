from tkinter import * #Interface Gráfica
import tkinter.ttk as ttk #Interface Gráfica
from tkinter import filedialog #Interface Gráfica
from tkinter import messagebox #Interface Gráfica
from Crypto.Hash import SHA256 #Gerar Hash
from tkinter import scrolledtext #Scroll para caixa de saída private e public key
from Crypto.PublicKey import RSA #Geração do par de chaves
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
import binascii
import io #leitura de arquivo txt
from os import path
import numpy as np #carregar imagem
from PIL import ImageTk #carregar imagem
import PIL.Image


def arquivo(msg):#abrir arquivo
    msg.clear()
    formats= [("Arquivo","*.txt")]
    arquivo = filedialog.askopenfilename(filetypes=formats,title='Selecione o arquivo para criptografia')
    try:
        linha = io.open(arquivo,"r", encoding="utf8")
    except:
        return
    texto=""
    for i in linha:
        texto+=i
    linha.close()
    messagebox.showinfo('Arquivo','Aquivo selecionado: '+str(path.basename(arquivo)))
    msg.append(texto)

def gerarChaves():#Gerador de chaves pública e privada
    limpaTela(FrameScroll)#limpa o frame caso tenha uma chave pública que já foi gerada
    limpaTela(FrameScroll2)#limpa o frame caso tenha uma assinatura digital que já foi gerada
    
    ##BEGIN FRAME ---- PUBLIC KEY --------
    publicKeyGenerate = Label(FrameScroll, text='Chave Pública:',font='arial 12 bold')
    publicKeyGenerate.pack()
    saida2 = scrolledtext.ScrolledText(FrameScroll,font="arial 15 normal",width=30,height=5,undo=True,state='normal')
    saida2.pack()
    ##END FRAME ---- PUBLIC KEY ---------
    
    keyPair = RSA.generate(1024)#criou-se o par de chave privada/pública.
    pubKey = keyPair.publickey()#Geração da chave pública
    priKey = keyPair.exportKey()#Geração da chave privada
    f = open('publickey.pem','wb')#salva chave pública em arquivo pem no diretório corrente
    f.write(pubKey.exportKey(format='PEM'))
    f.close()
    f = open('privatekey.pem','wb')#salva chave privada em arquivo pem no diretório corrente
    f.write(keyPair.exportKey(format='PEM'))
    f.close()
    entrada.delete(0,END)#Apaga se tiver alguma chave privada criada
    saida2.delete('1.0',END)#Apaga se tiver alguma chave pública criada
    entrada.insert(END,repr(keyPair.exportKey().decode("utf-8")).replace('-----BEGIN RSA PRIVATE KEY-----','').replace('-----END RSA PRIVATE KEY-----','').replace("'", ""))
    saida2.insert(END,repr(pubKey.exportKey().decode("utf-8")).replace('-----BEGIN PUBLIC KEY-----','').replace('-----END PUBLIC KEY-----','').replace("'", ""))
    pub.clear()
    pub.append(repr(pubKey.exportKey().decode("utf-8")).replace('-----BEGIN PUBLIC KEY-----','').replace('-----END PUBLIC KEY-----','').replace("'", ""))
    
   
def criptografiaHash(prikey,mensagem):#Gera o texto com a assinatura Digital // Recebe como parametros chave privada e texto em claro (arquivo.txt)
    if len(mensagem)==0:#Verifica se algum arquivo foi selecionado
        return messagebox.showwarning('Erro - Arquivo', 'Arquivo não foi selecionado!')
    prikey = '-----BEGIN PUBLIC KEY-----'+prikey+'-----END PUBLIC KEY-----'
    try:
        prikey = RSA.importKey(prikey.replace('\\n','\n'))
    except:
        return messagebox.showinfo('Inválida','Chave Inválida!')
    mensagem = mensagem[0]
    mensagem = bytes(mensagem, 'utf-8')#transforma a mensagem(string utf-8 para bytes)
    hash_ = SHA256.new(mensagem)#cria o hash da mensagem
    signer = PKCS115_SigScheme(prikey)#instancia o objeto para a assinatura
    signature = signer.sign(hash_)#faz assinatura digital em binasciis

    f = open('digitalSignature.pem','wb')#salva chave privada em arquivo pem no diretório corrente
    f.write(binascii.hexlify(signature))
    f.close()
    ass.clear()
    ass.append(binascii.hexlify(signature))


    limpaTela(FrameScroll2)#limpa o frame caso tenha uma assinatura digital que já foi gerada
    ##BEGIN FRAME ---- DIGITAL SIGNATURE --------
    digitalSignature = Label(FrameScroll2, text='Assinatura Digital:',font='arial 12 bold')
    digitalSignature.pack()
    saida3 = scrolledtext.ScrolledText(FrameScroll2,font="arial 15 normal",width=30,height=5,undo=True,state='normal')
    saida3.pack()
    saida3.insert(END,binascii.hexlify(signature))
    ##END FRAME ---- DIGITAL SIGNATURE ---------

    messagebox.showinfo('OK','Texto assinado com sucesso!')
    return signature #retorna a assinatura digital em binascii

def descriptografiaHash(pubKey,mensagem,assinatura):#Função que retorna verdadeiro ou falso dado a chave pública, mensagem e assinatura
    if len(mensagem)==0:#mensagem não foi selecionada
        return messagebox.showwarning('Erro - Arquivo', 'Arquivo não foi selecionado!')
    mensagem=mensagem[0]
    pubKey = '-----BEGIN PUBLIC KEY-----'+pubKey+'-----END PUBLIC KEY-----'
    try:
        pubKey = RSA.importKey(pubKey.replace('\\n','\n'))
        assinatura = binascii.unhexlify(assinatura)#transforma de hexadecimal para binascii
        mensagem = bytes(mensagem, 'utf-8')#transforma a mensagem(string utf-8 para bytes)
        hash_ = SHA256.new(mensagem)
        verifier = PKCS115_SigScheme(pubKey)
    except:
        mensagemDeValidacao["text"] = 'Falso'
        return
    try:
        verifier.verify(hash_, assinatura)
        mensagemDeValidacao["text"] = 'Verdadeiro'
    except:
        mensagemDeValidacao["text"] = 'Falso'
    

def criptografia(): #TELA - Assinar Arquivo 
    limpaTela()
    global saida,entrada,FrameScroll,FrameScroll2,pub,ass
    msg = []
    ass = []
    pub = []
    texto = Label(window, text='Criptografia de Arquivo',font='arial 12 normal')
    texto.pack()
    frame = Frame(window)
    frame.pack()
    privateKey = Label(frame, text='Chave Privada:',font='arial 12 bold')
    privateKey.grid(row = 0,column = 0)
    entrada = Entry(frame, font="arial 15 normal")
    entrada.grid(row=0,column=1)
    gerar = ttk.Button(frame, text="Gerar Chaves",command = gerarChaves)
    gerar.grid(row=0,column=2,padx=20)
    botaoArquivo = Button(window, text="Selecionar Arquivo",cursor="hand2",relief=RIDGE,command = lambda : arquivo(msg))
    botaoArquivo.pack(pady=10)
    botaoEnviar = ttk.Button(window, text="Enviar",command = lambda : criptografiaHash(entrada.get(),msg))
    botaoEnviar.pack(pady=(0,10))
    FrameScroll = Frame(window)
    FrameScroll.pack()
    FrameScroll2 = Frame(window)
    FrameScroll2.pack()

def gerador(k,entrada_): #função auxiliar para o preenchimento automático na Verificação de Assinatura
    if k=='a':#assinatura
        try:
            entrada_.delete(0,END)#Apaga se tiver alguma assinatura digital criada
            return entrada_.insert(END,ass[0])
        except:
            messagebox.showinfo('Assinatura','Assinatura não foi Gerada!')
    else:
        try:
            entrada_.delete(0,END)#Apaga se tiver alguma chave pública criada
            return entrada_.insert(END,pub[0])
        except:
            messagebox.showinfo('Chave Pública','Chave Pública não foi Gerada!')
    
def descriptografia(): #TELA - Verificar Arquivo
    limpaTela()
    global mensagemDeValidacao
    msg = []
    texto = Label(window, text='Verificação de Assinatura',font='arial 12 normal')
    texto.pack()
    frame = Frame(window)
    frame.pack()
    botaoArquivo = Button(window, text="Selecionar Arquivo",cursor="hand2",relief=RIDGE,command = lambda : arquivo(msg))
    botaoArquivo.pack(pady=10)
    pubKey = Label(frame, text='Chave Pública:',font='arial 12 bold')
    pubKey.grid(row = 0,column = 0,pady=5)
    entrada_pk = Entry(frame, font="arial 15 bold")
    entrada_pk.grid(row=0,column=1,pady=5)
    preencher = ttk.Button(frame, text="Preencher com Chave Gerada",command = lambda : gerador('p',entrada_pk),width = 30)
    preencher.grid(row=0,column=2,padx=20,pady=5)
    assinatura = Label(frame, text='Assinatura:',font='arial 12 bold')
    assinatura.grid(row = 1,column = 0)
    entrada_ad = Entry(frame, font="arial 15 bold")
    entrada_ad.grid(row=1,column=1)
    preencher2 = ttk.Button(frame, text="Preencher com Assinatura Gerada",command = lambda : gerador('a',entrada_ad),width = 30)
    preencher2.grid(row=1,column=2,padx=20)
    botaoEnviar = ttk.Button(window, text="Enviar",command = lambda: descriptografiaHash(entrada_pk.get(),msg,entrada_ad.get()))
    botaoEnviar.pack()
    mensagemDeValidacao = Label(window, text="", font="impact 20 bold")
    mensagemDeValidacao.pack()
    
def home():
    limpaTela()
    imagem = np.asarray(imagem)
    imagem = ImageTk.PhotoImage(PIL.Image.fromarray(imagem.astype(np.uint8)))
    w = Label(window, image=imagem)
    w.imagem = imagem
    w.pack()

def all_children (window) :
    _list = window.winfo_children()
    for item in _list :
        if item.winfo_children() :
            _list.extend(item.winfo_children())
    return _list

def limpaTela(tela = ''):
    if tela=='':
        tela = window
    widget_list = all_children(tela)
    for item in widget_list:
        item.pack_forget()
    
#############MAIN#####################
window = Tk()
menu = Menu(window)
window.config(menu=menu)
menu.add_cascade(label='Home',command=home)
menu.add_cascade(label='Assinar Arquivo',command=criptografia)
menu.add_cascade(label='Verificar Arquivo',command=descriptografia)
home()
window.title('Assinatura Digital - Filipe / João Lucas / Rodrigo')
window.geometry('700x500+200+100')#altura x largura + eixo_x + eixo_y
window.mainloop()
################################