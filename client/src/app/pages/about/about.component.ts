// src/app/pages/about/about.component.ts

import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';


@Component({
  selector: 'app-about',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatCardModule,
   
  ],
  templateUrl: './about.component.html',
  styleUrl: './about.component.css'
})
export class AboutComponent {
  
  teamMembers = [
    {
      name: 'Ján Novák',
      position: 'Zakladateľ & CEO',
      image: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400',
      description: 'Viac ako 15 rokov skúseností v hotelierstve a správe nehnuteľností.'
    },
    {
      name: 'Mária Kováčová',
      position: 'Manažérka prevádzky',
      image: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400',
      description: 'Stará sa o bezproblémový chod všetkých apartmánov a spokojnosť hostí.'
    },
    {
      name: 'Peter Horváth',
      position: 'Zákaznícky servis',
      image: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400',
      description: 'K dispozícii 24/7 pre akékoľvek otázky a požiadavky našich hostí.'
    }
  ];

}
