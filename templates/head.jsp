<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

    <div class="head">
        <div class="top">
            <div >
                <a href="ListaRutas.do"><img class="logo" src="${pageContext.request.contextPath}/images/logo.png" alt="Nuestro logo"></a>
            </div>
            <div class="topMenu">
                <div class="search">
                    <form action="BuscarRuta.do">
                    <input type="search" placeholder="Búsca el chollo" name="search">
                    </form>
                </div>
                <div class="addchollo">
                    <a href='<c:url value="/AddRuta.do"></c:url>'><button>Añadir ruta</button></a>
                </div>
                <c:if test="${empty sesion}"> 
                <div class="Registro">
                    <a href="Registro.do"><button>Registrate</button></a>
                </div>
                </c:if>
            </div>
            <div class="nombrePagina">
              <h1>Hobbit Feet</h1>
            </div>
        </div>
        <div class="navegacionwarp">
            <nav class="menu">
            	<ul>
            		<li><a href="ListaRutas.do">Inicio</a></li>
            		<li> <a class = "linkcat">Categorí­as</a>
            			<ul class="submenu">
            				<c:forEach var="categoria" items="${categoriasList}">
            				<li><a href="<c:url value='RutasCategoria.do?id=${categoria.id }'/>" >${categoria.name}</a></li>
            				</c:forEach>   		
            			</ul>
            			</li>
            		<li> <a class = "linkshop">Dificultad</a>
            			<ul class="submenuT">
            				<li><a href="RouteDifficult.do?difficult=easy" >Fácil</a></li>
            				<li><a href="RouteDifficult.do?difficult=medium" >Medio</a></li>
            				<li><a href="RouteDifficult.do?difficult=hard" >Difícil</a></li>
            			</ul>
            			</li>
             		<li><a href="<c:url value='OrdenarKudos.do'/>">Mas kudos primero</a></li>
	   				<li><a href="<c:url value='QuitarBlocked.do'/>">Solo rutas disponibles</a></li>
	   				<li><form action="MinLikes.do"><input type="submit" value="Mostrar chollos con like minimo"><input type="number" name="minKudos" min="0" value="1"></form></li>
            	</ul>        
			</nav>
        </div>
        </div>
