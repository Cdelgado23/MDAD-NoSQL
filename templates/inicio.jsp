<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html lang="es">  
   <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" >
        <title>Hobbit Feet</title>
        <link rel="stylesheet" type="text/css" href="${pageContext.request.contextPath}/css/index.css">
    </head>
        <body>
	   <c:import url="head.jsp"/>
       <div class="centro">
        <div class="listachollos">
        	<c:forEach var="route" items="${routesList}">
        	<div class="chollazo">
        	<div class="
        	<c:choose>
        	<c:when test="${route.first.blocked==0}">
            chollo
            </c:when>
            <c:otherwise>
			cholloSO
            </c:otherwise>
            </c:choose>">
                <div class="derechaChollo">
                	<c:choose>
                	<c:when test="${route.first.blocked==0}">
                    <img class="fotochollo" src="${pageContext.request.contextPath}/images/ruta.jpg" alt="Foto del chollo">
                	</c:when>
                	<c:otherwise>
                	 <img class="fotochollo" src="${pageContext.request.contextPath}/images/x.png" alt="Foto del chollo">              	
                	</c:otherwise>
                	</c:choose>
                	<c:forEach var="category" items="${route.third}">
                	<p>${category}</p>
                	</c:forEach>
                    <p>By: ${route.second.username }</p>
                </div>
                <div class="cuerpochollo">
                    <div class="nombreChollo">
                        <p>${route.first.title}</p>
                    </div>
                    <div class="precio">
                        <p>Longitud: ${route.first.distance} km </p>
                        <p>Elevación: ${route.first.elevation} m</p>
                        <p>Duración: ${route.first.duracion} h</p>
                        <p class="
        				<c:choose>
        				<c:when test="${route.first.done<100}">
            			menos100
            			</c:when>
           				<c:otherwise>
						mas100
            			</c:otherwise>
           				 </c:choose>">Hecho ${route.first.done} veces</p>
                        <p>${route.first.date}</p>                        
                    </div>
                    <div>
                    <p>${route.first.difficult}</p>
                    </div>
                    <div class="descripcionchollo">
                        <p>${route.first.description}</p>
                    </div>
                    <div class="piechollo">
                        <div class="likes">
                        	<img alt="Me gustas" src="${pageContext.request.contextPath}/images/mg.png">${route.first.kudos} 
                            <a href="<c:url value='Kudo.do?idr=${route.first.id}'/>"><button><img alt="like" src="${pageContext.request.contextPath}/images/like.png"></button></a>
                            <a href="<c:url value='DesKudo.do?idr=${route.first.id}'/>"><button><img alt="dislike" src="${pageContext.request.contextPath}/images/dislike.png"></button></a>
                        </div>
                    </div>
                </div>
            <c:if test="${route.first.idu == sesion.id}">
            <div class="accionesChollo">
            <a href="<c:url value='DeleteRuta.do?idr=${route.first.id}'/>"><button>Borrar</button></a>
            <a href="<c:url value='EditarRuta.do?idr=${route.first.id}'/>"><button>Editar</button></a>
            <c:choose>
              	<c:when test="${route.first.blocked==0}">
				<a href="<c:url value='BloquearRuta.do?idr=${route.first.id}'/>"><button>Bloquear</button></a>
				</c:when>        	
                	<c:otherwise>
                	<a href="<c:url value='DesbloquearRuta.do?idr=${route.first.id}'/>"><button>Desbloquear</button></a>
  	            	</c:otherwise>
                </c:choose>         
            </div>            
            </c:if>           
            </div><!-- hola -->          
            </div>
            </c:forEach>
        </div>
        </div>
           <div class="acceso">
           <c:choose>
           <c:when test="${empty sesion}"> 
               <fieldset>
                   <legend>Acceso</legend>
                <form action="LogIn.do" method="POST">
                    <p>Usuario</p>
                    <input type="text" placeholder="User" name="user">
                    <p>Contraseña</p>
                    <input type="password" placeholder="password" name="pass">
                    <p><input type="submit" value="Log in"></p>
               </form>
                    <p><a href="Registro.do"><button>Sign in</button></a></p>
               </fieldset>
            </c:when>
            <c:otherwise>
            <fieldset>
            	<legend>${sesion.username}</legend>
            	<img alt="user" src="${pageContext.request.contextPath}/images/user.jpeg" class="user-img">
            	<ul class="Perfil">
            		<li><a href="<c:url value='RutasUser.do?id=${sesion.id}'/>" > Mis Rutas</a></li>
            		<li><a href="<c:url value='LogOut.do'/>">Desconectarse </a></li>
            		<li><a href="<c:url value='EditUser.do?id=${sesion.id}'/>">Editar perfil</a></li>
            		<li><a href="<c:url value='DeleteUser.do?id=${sesion.id}'/>">Eliminar perfil</a></li>
            	</ul>
            </fieldset>
            </c:otherwise>
            </c:choose>
           </div>     
    </body>


</html>