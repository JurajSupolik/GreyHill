import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // Získaj token z localStorage
  const token = localStorage.getItem('access_token');

  // Ak existuje token, pridaj ho do headeru
  if (token) {
    const clonedReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
    return next(clonedReq);
  }

  // Inak pošli request bez tokenu
  return next(req);
};
