# Restaure les options et les contraintes anti-double-réservation de RDV.
# La migration 0002 les avait supprimées à cause d'un bug d'indentation qui
# détachait la classe Meta du modèle RDV (Meta orpheline au niveau module).
# Le modèle étant corrigé, on réapplique : options + contrainte docteur +
# contrainte patient (cette dernière n'avait jamais été migrée).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0002_alter_rdv_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rdv',
            options={
                'ordering': ['-date', '-heure'],
                'verbose_name': 'Rendez-vous',
                'verbose_name_plural': 'Rendez-vous',
            },
        ),
        migrations.AddConstraint(
            model_name='rdv',
            constraint=models.UniqueConstraint(
                fields=('docteur', 'date', 'heure'),
                name='unique_rdv_creneau_docteur',
            ),
        ),
        migrations.AddConstraint(
            model_name='rdv',
            constraint=models.UniqueConstraint(
                fields=('patient', 'date', 'heure'),
                name='unique_rdv_creneau_patient',
            ),
        ),
    ]
