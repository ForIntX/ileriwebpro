from django.core.management.base import BaseCommand
from core.models import Polyclinic, Doctor


class Command(BaseCommand):
    help = 'Demo veriyi yükler: 3 poliklinik ve 3 doktor.'

    def handle(self, *args, **options):
        self.stdout.write('Demo veri oluşturuluyor...')

        # Poliklinikler
        dahiliye, created = Polyclinic.objects.get_or_create(
            name='Dahiliye',
            defaults={'floor': 'Kat 2', 'is_active': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Poliklinik: Dahiliye (Kat 2)'))
        else:
            self.stdout.write('  · Dahiliye zaten mevcut.')

        cerrahi, created = Polyclinic.objects.get_or_create(
            name='Cerrahi',
            defaults={'floor': 'Kat 3', 'is_active': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Poliklinik: Cerrahi (Kat 3)'))
        else:
            self.stdout.write('  · Cerrahi zaten mevcut.')

        acil, created = Polyclinic.objects.get_or_create(
            name='Acil',
            defaults={'floor': 'Kat 1', 'is_active': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Poliklinik: Acil (Kat 1)'))
        else:
            self.stdout.write('  · Acil zaten mevcut.')

        # Doktorlar
        _, created = Doctor.objects.get_or_create(
            full_name='Dr. Ayşe Demir',
            defaults={'polyclinic': dahiliye, 'room_number': '205', 'is_active': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Doktor: Dr. Ayşe Demir (Dahiliye, Oda 205)'))
        else:
            self.stdout.write('  · Dr. Ayşe Demir zaten mevcut.')

        _, created = Doctor.objects.get_or_create(
            full_name='Dr. Mehmet Kaya',
            defaults={'polyclinic': cerrahi, 'room_number': '310', 'is_active': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Doktor: Dr. Mehmet Kaya (Cerrahi, Oda 310)'))
        else:
            self.stdout.write('  · Dr. Mehmet Kaya zaten mevcut.')

        _, created = Doctor.objects.get_or_create(
            full_name='Dr. Zeynep Yılmaz',
            defaults={'polyclinic': acil, 'room_number': '101', 'is_active': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Doktor: Dr. Zeynep Yılmaz (Acil, Oda 101)'))
        else:
            self.stdout.write('  · Dr. Zeynep Yılmaz zaten mevcut.')

        self.stdout.write(self.style.SUCCESS('\nDemo veri başarıyla yüklendi!'))
