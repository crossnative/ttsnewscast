import { Routes } from '@angular/router';
import { StartPage } from './pages/start-page/start-page.component';
import { ReaderPage } from './pages/reader-page/reader-page.component';

export const routes: Routes = [
    {
        path: '',
        component: StartPage
    },
    {
        path: 'read',
        component: ReaderPage
    },
    {
        path: '**',
        redirectTo: ''
    }
];
