import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TestApiComponent } from '../../components/test-api/test-api.component';

@Component({
  selector: 'app-test',
  standalone: true,
  imports: [CommonModule, TestApiComponent],
  templateUrl: './test.component.html',
  styleUrls: ['./test.component.css']
})
export class TestComponent {
}
