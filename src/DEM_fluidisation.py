
import random as rd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider

#variables concernant un grain de sable
rp = 2e-3 #rayon des grains en m
N = 300 #nombre de grains
m = 9e-6 #masse d'un grain (kg)

#création de la figure
fig, ax = plt.subplots()
fig.canvas.manager.set_window_title("Simulation")
x_lim,y_lim = (6e-2,1.5e-1)
fig.set_size_inches(4,8)
ax.set_xlim(-rp, x_lim + rp)
ax.set_ylim(-rp, y_lim + rp)
plt.xlabel("abscisse x et ordonnée y en mètres")
plt.title("simulation de "+str(N)+" grains")

for i in range(int(x_lim/(2*rp)) + 1):
    plt.plot([i*2*rp,i*2*rp],[0,y_lim], "--", color = "#8099b2")
for i in range(int(y_lim/(2*rp)) + 1):
    plt.plot([0,x_lim],[i*2*rp,i*2*rp], "--", color = "#8099b2")

#variables temporelles
t = 0 #initialisation du temps
dt = 3e-4 #dt faible pour que la simulation soit cohérente

#expressions déduites du PFD pour qu'il y ait peu d'oscillations:
Q = 0.65 #faibles oscillations
epsilon = 0.015 #coefficient qui augmente la raideur car sinon les grains s'enfoncent trop entre eux (c'est toujours le cas même avec epsilon)
g = 9.81

#valeurs des coefficients de frottement gamma et de constante de raideur K des grains et de la paroi:
Kg = m*g/(epsilon*rp)  
Kp = m*g/(epsilon*rp) 
gamma_g = np.sqrt(m*Kg)/Q
gamma_p = np.sqrt(m*Kp)/Q

#loi de Darcy et Karman-Kozeni:
V = 0 #vitesse du fluide (modifiable pendant la simulation dans la console)
A = 150 #coefficient utilisé dans le calcul de la fraction volumique phi cf Les milieux granulaires: Entre fluide et solide
nu = 1.8e-5 #coefficient de viscosité dynamique de l'air
rho_air = 1.2e-3
phi = np.zeros(N)

#position, vitesse, acceleration:
X = np.array([rd.uniform(5*rp,x_lim - 5*rp) for k in range(N)])
Y = np.array([rd.uniform(5*rp, y_lim - 5*rp) for k in range(N)])
Vx,Vy = np.zeros(N), np.zeros(N)
Ax,Ay = np.zeros(N), np.zeros(N)

#stockage des grains dans une liste
Gn = [] #Grains
for i in range(N):
        grain = plt.Circle((X[i],Y[i]), rp, facecolor = rd.choice(["#62c1ff","#2b8eff"]), edgecolor="#0082ca", fill=True)
        ax.add_patch(grain)
        Gn.append(grain)
    
def tri_case(X,Y):
    #tri en O(N) 
    n = len(X)
    p,q = int(x_lim/(2*rp)), int(y_lim/(2*rp))  + 1
    Lg = [[[] for j in range(q)] for i in range(p)] #tableau dont chaque case correspond à un carré de longueure rp
    for k in range(n): #on place chaque grain dans sa case correspondante en fonction de ses coordonnées
        i,j = int(X[k]//(2*rp)),int(Y[k]//(2*rp))
        Lg[i][j].append(k) 
    return Lg

def dist_2(x1,x2,y1,y2): #distance euclidienne au carré O(1)
    return (x1 - x2)**2 + (y1 - y2)**2
        
def colisions_grain(Cn,Lg,X,Y,x,y,grain_i): #O(1) car on regarde seulement les grains voisins
    lim_x,lim_y = len(Lg),len(Lg[0])
    dp_carre = 4*rp**2
    
    #pour un grain i donnée: étude des cases voisines qui sont dans le cadre de la figure
    for p in (-1,0,1):
        for q in (-1,0,1):
            if x + p >= 0 and x + p < lim_x and y + q >= 0 and y + q < lim_y:
                
                #étude de caque grain contenu dans la case
                for grain_j in Lg[x+p][y+q]:
                    if grain_i != grain_j and grain_j not in Cn[grain_i] and dist_2(X[grain_i],X[grain_j],Y[grain_i],Y[grain_j]) <= dp_carre:
                        #si il y a contact, on ajoute la colision entre i et j dans le dictionnaire
                        Cn[grain_i].append(grain_j)
                        Cn[grain_j].append(grain_i)
            

def colisions(X,Y,rp): #O(N)
    #on trie chaque grain dans la case qui lui correspond
    Lg = tri_case(X,Y) #O(N)
    
    #chaque grain peut entrer en colision avec les grains des cases voisines
    N = len(X)
    Cn = [[] for i in range(N)] #liste des colisions
    
    #boucle en O(N)
    for x in range(len(Lg)):
        for y in range(len(Lg[x])):
            for grain_i in Lg[x][y]:
                #on étudie les colisions pour chaque grain
                colisions_grain(Cn,Lg,X,Y,x,y,grain_i) #O(1)
    return Cn,Lg
   

def force_grains(i,j,Vx,Vy,X,Y): #ressort + frottement normal et tangentiel

    dx, dy = (X[j] - X[i]), (Y[j] - Y[i])
    alpha = np.arctan2(dy, dx)  # Angle entre les grains
    v_rel_x = Vx[i] - Vx[j]
    v_rel_y = Vy[i] - Vy[j]
    
    # Projection de la vitesse relative dans la direction normale et tangentielle
    v_n = v_rel_x*np.cos(alpha) + v_rel_y*np.sin(alpha)
    v_t = -v_rel_x*np.sin(alpha) + v_rel_y*np.cos(alpha)

    d = np.sqrt(dx**2 + dy**2)
    
    Fn = -Kg*(2.25*rp - d) - gamma_g*v_n 
    Ft = -gamma_g*v_t
    
    return Fn, Ft, alpha

def maj_phi(Lg,X,Y,i):
    x,y = int(X[i]//(2*rp)),int(Y[i]//(2*rp))
    lim_x,lim_y = len(Lg),len(Lg[0])
    N_grains_voisins = 0
    N_cases = 0
    for p in (-1,0,1):
        for q in (-1,0,1):
            if x + p >= 0 and x + p < lim_x and y + q >= 0 and y + q < lim_y:
                N_grains_voisins += len(Lg[x+p][y+q])
                N_cases += 1

    #on détermine le volume occupé uniquement par les grains
    Vg = N_grains_voisins*4*np.pi*rp**3
    
    #on détermine le volume occupé par les grains et l'air
    V0 = 3*N_cases*(2*rp)**3
    
    return Vg/V0

def maj_k(phi_grain):
    return ((2*rp)**2)*((1-phi_grain)**3)/(A*(phi_grain**2)) #calcul de phi (fraction volumique) dans un milieu dense cf Les milieux granulaires: Entre fluide et solide

def force_fluide_gradient_pression(i,Lg,X,Y):
    phi[i] = maj_phi(Lg,X,Y,i)
    k = maj_k(phi[i])
    #loi de Darcy: Les milieux granulaires: Entre fluide et solide
    return rho_air*g + (nu/k)*V 

def conditions_limites(x,y,vxi,vyi,fxi,fyi): #pour éviter que des grains sortent du cadre
    if x > x_lim - rp:
        vxi,fxi = -vxi, -abs(Kp*(x_lim - rp - x)) - gamma_p*vxi
    elif x < rp:
        vxi,fxi = -vxi, abs(Kp*(rp - x)) - gamma_p*vxi
    if y < rp:
        vyi,fyi = -vyi, abs(Kp*(y - rp)) - gamma_p*vyi
    elif y > y_lim - rp:
        vyi,fyi = -vyi, -abs(Kp*(y_lim - rp - y)) - gamma_p*vyi
    return vxi,vyi,fxi,fyi

def forces(X,Y,Vx,Vy):
    #on détermine les colisions qui existent entre les grains
    Cn,Lg = colisions(X,Y,rp)

    #initialisation des forces
    Fx,Fy = np.zeros(N), np.zeros(N)
    Fy += - m*g
    
    #on ajoute les forces entre chaque grain qui sont en colision
    for i in range(N):
        for j in Cn[i]:
            Fn,Ft,alpha = force_grains(i,j,Vx,Vy,X,Y)
            Fx[i] += Fn*np.cos(alpha) - Ft*np.sin(alpha)
            Fy[i] += Fn*np.sin(alpha) + Ft*np.cos(alpha)
            
        #on rajoute la force exercée par le fluide dans le milieu poreux sur chaque grain
        Pf = force_fluide_gradient_pression(i,Lg,X,Y)
        Fy[i] += Pf*(4/3)*np.pi*rp**3
        
        #conditions aux limites: parois laterales et horizontales
        Vx[i],Vy[i],Fx[i],Fy[i] = conditions_limites(X[i],Y[i],Vx[i],Vy[i],Fx[i],Fy[i])
            
    return Fx, Fy

def integration(X,Y,Vx,Vy,Ax,Ay): #intégration par méthode de Verlet car Euler est instable (sujet modélisation mines pont) 
    
    #nouvelles listes d'acceleration, de vitesse, de position
    Ax2, Ay2 = np.zeros(N), np.zeros(N)
    Vx2, Vy2 = np.zeros(N), np.zeros(N)
    X2, Y2 = np.zeros(N), np.zeros(N)
    
    #intégration Verlet
    Vx_demi, Vy_demi = Vx + 0.5*dt*Ax, Vy + 0.5*dt*Ay
    X2, Y2 = X + dt*Vx_demi, Y + dt*Vy_demi
    Fx, Fy = forces(X2, Y2, Vx_demi, Vy_demi)
    Ax2, Ay2 = Fx/m, Fy/m
    Vx2, Vy2 = Vx_demi + 0.5*dt*Ax2, Vy_demi + 0.5*dt*Ay2
    
    return Ax2,Ay2,Vx2,Vy2,X2,Y2

def maj(frame):
    global Ax,Ay,Vx,Vy,X,Y,rp,t,V
    
    #nouvelles positions au temps t + dt
    Ax,Ay,Vx,Vy,X,Y = integration(X,Y,Vx,Vy,Ax,Ay)
    
    for i,grain in enumerate(Gn):
        grain.set_center((X[i], Y[i]))
    t += dt
    
    return Gn

plt.rcParams['toolbar'] = 'None'
# Fenêtre plus petite et compacte
fig_ctrl = plt.figure("Contrôle des paramètres", figsize=(4.5, 3.5), facecolor='#1e272e')
fig_ctrl.suptitle("CONTRÔLES PHYSIQUES", fontsize=11, fontweight='bold', color='#d2dae2', x=0.5, y=0.92)

# Couleurs
slider_bg = '#2f3640' 
accent_v   = '#3498db' # Vitesse
accent_m   = '#e67e22' # Masse
accent_rho = '#2ecc71' # Rho
accent_nu  = '#9b59b6' # Viscosité

def create_mini_slider(pos_y, label, color):
    fig_ctrl.text(0.1, pos_y + 0.05, label, color='white', fontsize=8, fontweight='bold')
    ax = fig_ctrl.add_axes([0.1, pos_y, 0.65, 0.025], facecolor=slider_bg)
    return ax

ax_v   = create_mini_slider(0.56, "Vitesse du Fluide (V)", accent_v)
ax_m   = create_mini_slider(0.72, "Masse Individuelle d'un Grain (m)", accent_m)
ax_rho = create_mini_slider(0.36, "Densité du Fluide (ρ)", accent_rho)
ax_nu  = create_mini_slider(0.18, "Viscosité du Fluide (ν)", accent_nu)

# Sliders
s_v   = Slider(ax_v, '', 0.0, 10.0, valinit=V, valfmt='%1.1f m.s-1', color=accent_v)
s_m   = Slider(ax_m, '', 1e-6, 5e-5, valinit=m, valfmt='%1.0e kg', color=accent_m)
s_rho = Slider(ax_rho, '', 0.5, 2.5, valinit=1.225, valfmt='%1.2f kg.m-3', color=accent_rho)
s_nu  = Slider(ax_nu, '', 1e-6, 1e-4, valinit=1.5e-5, valfmt='%1.0e PI', color=accent_nu)

for s in [s_v, s_m, s_rho, s_nu]:
    s.valtext.set_color('white')
    s.valtext.set_fontsize(8)
    s.valtext.set_fontweight('bold')

def update_params(val):
    global V, m, rho_air, nu, Kg, Kp, gamma_g, gamma_p
    V, m, rho_air, nu = s_v.val, s_m.val, s_rho.val, s_nu.val
    
    # Recalculs physiques
    Kg = m * 9.81 / (epsilon * rp)
    Kp = Kg
    gamma_g = np.sqrt(m * Kg) / Q
    gamma_p = np.sqrt(m * Kp) / Q
    
    fig_ctrl.canvas.draw_idle()

s_v.on_changed(update_params)
s_m.on_changed(update_params)
s_rho.on_changed(update_params)
s_nu.on_changed(update_params)

plt.subplots_adjust(left=0.1)

ani = animation.FuncAnimation(fig, maj, frames=1, interval=dt*1e3, blit=True)
plt.show()
