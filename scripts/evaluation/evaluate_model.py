"""
Comprehensive model evaluation script.
Compares your CNN against other models and provides detailed metrics.
"""
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    roc_curve, auc
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import label_binarize
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import os
from src.gesture_cnn import GestureCNN, create_training_data_from_landmarks
from scripts.training.train_model import load_dataset_from_file, generate_synthetic_data


class ModelEvaluator:
    """Evaluate and compare multiple models."""
    
    GESTURE_CLASSES = [
        'move_cursor', 'left_click', 'right_click',
        'scroll', 'drag', 'thumbs_up'
    ]
    
    def __init__(self, X_test, y_test, y_test_labels):
        """
        Args:
            X_test: Test features (N, 63)
            y_test: Test labels one-hot encoded (N, 6)
            y_test_labels: Test labels as integers (N,)
        """
        self.X_test = X_test
        self.y_test = y_test
        self.y_test_labels = y_test_labels
        self.results = {}
    
    def evaluate_cnn(self, model_path='models/gesture_cnn.h5'):
        """Evaluate your CNN model."""
        print("\n" + "="*60)
        print("Evaluating CNN Model")
        print("="*60)
        
        cnn = GestureCNN(model_path=model_path)
        
        # Get predictions
        predictions = cnn.model.predict(self.X_test, verbose=0)
        y_pred = np.argmax(predictions, axis=1)
        
        # Calculate metrics
        metrics = self._calculate_metrics(self.y_test_labels, y_pred, predictions)
        self.results['CNN'] = {
            'model': cnn,
            'predictions': y_pred,
            'probabilities': predictions,
            'metrics': metrics
        }
        
        self._print_metrics('CNN', metrics)
        return metrics
    
    def evaluate_random_forest(self):
        """Evaluate Random Forest baseline."""
        print("\n" + "="*60)
        print("Evaluating Random Forest (Baseline)")
        print("="*60)
        
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(self.X_test, self.y_test_labels)
        
        y_pred = rf.predict(self.X_test)
        probabilities = rf.predict_proba(self.X_test)
        
        metrics = self._calculate_metrics(self.y_test_labels, y_pred, probabilities)
        self.results['Random Forest'] = {
            'model': rf,
            'predictions': y_pred,
            'probabilities': probabilities,
            'metrics': metrics
        }
        
        self._print_metrics('Random Forest', metrics)
        return metrics
    
    def evaluate_svm(self):
        """Evaluate SVM."""
        print("\n" + "="*60)
        print("Evaluating SVM (Support Vector Machine)")
        print("="*60)
        
        svm = SVC(kernel='rbf', probability=True, random_state=42)
        svm.fit(self.X_test, self.y_test_labels)
        
        y_pred = svm.predict(self.X_test)
        probabilities = svm.predict_proba(self.X_test)
        
        metrics = self._calculate_metrics(self.y_test_labels, y_pred, probabilities)
        self.results['SVM'] = {
            'model': svm,
            'predictions': y_pred,
            'probabilities': probabilities,
            'metrics': metrics
        }
        
        self._print_metrics('SVM', metrics)
        return metrics
    
    def evaluate_knn(self, k=5):
        """Evaluate k-Nearest Neighbors."""
        print("\n" + "="*60)
        print(f"Evaluating kNN (k={k})")
        print("="*60)
        
        knn = KNeighborsClassifier(n_neighbors=k)
        knn.fit(self.X_test, self.y_test_labels)
        
        y_pred = knn.predict(self.X_test)
        probabilities = knn.predict_proba(self.X_test)
        
        metrics = self._calculate_metrics(self.y_test_labels, y_pred, probabilities)
        self.results['kNN'] = {
            'model': knn,
            'predictions': y_pred,
            'probabilities': probabilities,
            'metrics': metrics
        }
        
        self._print_metrics('kNN', metrics)
        return metrics
    
    def evaluate_decision_tree(self):
        """Evaluate Decision Tree."""
        print("\n" + "="*60)
        print("Evaluating Decision Tree")
        print("="*60)
        
        dt = DecisionTreeClassifier(random_state=42)
        dt.fit(self.X_test, self.y_test_labels)
        
        y_pred = dt.predict(self.X_test)
        probabilities = dt.predict_proba(self.X_test)
        
        metrics = self._calculate_metrics(self.y_test_labels, y_pred, probabilities)
        self.results['Decision Tree'] = {
            'model': dt,
            'predictions': y_pred,
            'probabilities': probabilities,
            'metrics': metrics
        }
        
        self._print_metrics('Decision Tree', metrics)
        return metrics
    
    def _calculate_metrics(self, y_true, y_pred, probabilities):
        """Calculate all evaluation metrics."""
        metrics = {}
        
        # Basic metrics
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['precision'] = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        metrics['recall'] = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        metrics['f1'] = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Per-class metrics
        metrics['classification_report'] = classification_report(
            y_true, y_pred, labels=list(range(len(self.GESTURE_CLASSES))), 
            target_names=self.GESTURE_CLASSES, output_dict=True, zero_division=0
        )
        
        # Confusion matrix
        metrics['confusion_matrix'] = confusion_matrix(
            y_true, y_pred, labels=list(range(len(self.GESTURE_CLASSES)))
        )
        
        # ROC-AUC
        try:
            y_bin = label_binarize(y_true, classes=range(len(self.GESTURE_CLASSES)))
            metrics['roc_auc'] = roc_auc_score(y_bin, probabilities, average='weighted', multi_class='ovr')
        except:
            metrics['roc_auc'] = None
        
        return metrics
    
    def _print_metrics(self, model_name, metrics):
        """Print metrics in readable format."""
        print(f"\n{model_name} Performance:")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1-Score:  {metrics['f1']:.4f}")
        if metrics['roc_auc']:
            print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
        
        print(f"\nPer-class breakdown:")
        for class_name in self.GESTURE_CLASSES:
            if class_name in metrics['classification_report']:
                report = metrics['classification_report'][class_name]
                print(f"  {class_name:15} - P: {report['precision']:.3f}, R: {report['recall']:.3f}, F1: {report['f1-score']:.3f}")
    
    def plot_comparison(self, output_dir='results/'):
        """Create comparison visualizations."""
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Accuracy comparison
        plt.figure(figsize=(10, 6))
        models = list(self.results.keys())
        accuracies = [self.results[m]['metrics']['accuracy'] for m in models]
        colors = ['#2ecc71' if m == 'CNN' else '#3498db' for m in models]
        
        bars = plt.bar(models, accuracies, color=colors)
        plt.ylabel('Accuracy', fontsize=12)
        plt.title('Model Accuracy Comparison', fontsize=14, fontweight='bold')
        plt.ylim([0, 1])
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{output_dir}accuracy_comparison.png', dpi=300)
        print(f"Saved: {output_dir}accuracy_comparison.png")
        plt.close()
        
        # 2. Metrics comparison
        plt.figure(figsize=(12, 6))
        metrics_list = ['accuracy', 'precision', 'recall', 'f1']
        x = np.arange(len(models))
        width = 0.2
        
        for i, metric in enumerate(metrics_list):
            values = [self.results[m]['metrics'][metric] for m in models]
            plt.bar(x + i*width, values, width, label=metric.capitalize())
        
        plt.xlabel('Model', fontsize=12)
        plt.ylabel('Score', fontsize=12)
        plt.title('Comprehensive Metrics Comparison', fontsize=14, fontweight='bold')
        plt.xticks(x + width * 1.5, models, rotation=45)
        plt.legend()
        plt.ylim([0, 1])
        plt.tight_layout()
        plt.savefig(f'{output_dir}metrics_comparison.png', dpi=300)
        print(f"Saved: {output_dir}metrics_comparison.png")
        plt.close()
        
        # 3. Confusion matrices
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for idx, (model_name, result) in enumerate(self.results.items()):
            cm = result['metrics']['confusion_matrix']
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                       xticklabels=self.GESTURE_CLASSES, yticklabels=self.GESTURE_CLASSES)
            axes[idx].set_title(f'{model_name}')
            axes[idx].set_ylabel('True Label')
            axes[idx].set_xlabel('Predicted Label')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}confusion_matrices.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {output_dir}confusion_matrices.png")
        plt.close()
    
    def summary_report(self, output_file='results/evaluation_report.txt'):
        """Generate comprehensive evaluation report."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("GESTURE MOUSE - MODEL EVALUATION REPORT\n")
            f.write("="*70 + "\n\n")
            
            # Summary table
            f.write("SUMMARY COMPARISON\n")
            f.write("-"*70 + "\n")
            f.write(f"{'Model':<20} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1':<12}\n")
            f.write("-"*70 + "\n")
            
            for model_name in sorted(self.results.keys()):
                metrics = self.results[model_name]['metrics']
                f.write(f"{model_name:<20} {metrics['accuracy']:<12.4f} "
                       f"{metrics['precision']:<12.4f} {metrics['recall']:<12.4f} "
                       f"{metrics['f1']:<12.4f}\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("DETAILED REPORTS\n")
            f.write("="*70 + "\n\n")
            
            for model_name in sorted(self.results.keys()):
                f.write(f"\n{model_name}\n")
                f.write("-"*70 + "\n")
                metrics = self.results[model_name]['metrics']
                
                f.write(f"Accuracy:  {metrics['accuracy']:.4f}\n")
                f.write(f"Precision: {metrics['precision']:.4f}\n")
                f.write(f"Recall:    {metrics['recall']:.4f}\n")
                f.write(f"F1-Score:  {metrics['f1']:.4f}\n")
                if metrics['roc_auc']:
                    f.write(f"ROC-AUC:   {metrics['roc_auc']:.4f}\n")
                
                f.write(f"\nPer-class Performance:\n")
                for class_name in self.GESTURE_CLASSES:
                    if class_name in metrics['classification_report']:
                        report = metrics['classification_report'][class_name]
                        f.write(f"  {class_name:<15} - P: {report['precision']:.3f}, "
                               f"R: {report['recall']:.3f}, F1: {report['f1-score']:.3f}\n")
        
        print(f"Report saved to: {output_file}")


def main():
    """Run comprehensive evaluation."""
    print("Loading dataset...")
    
    # Load or generate dataset
    dataset_path = 'data/training_dataset.pkl'
    landmarks_list, labels = load_dataset_from_file(dataset_path)
    
    if landmarks_list is None:
        print("Generating synthetic data...")
        landmarks_list, labels = generate_synthetic_data(num_samples_per_class=200)
    
    # Create training data
    X, y = create_training_data_from_landmarks(landmarks_list, labels)
    
    # Split: 80% train, 20% test
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    y_test_labels = np.argmax(y_test, axis=1)
    
    print(f"Test set size: {len(X_test)} samples\n")
    
    # Initialize evaluator
    evaluator = ModelEvaluator(X_test, y_test, y_test_labels)
    
    # Evaluate all models
    evaluator.evaluate_cnn()
    evaluator.evaluate_decision_tree()
    evaluator.evaluate_random_forest()
    evaluator.evaluate_svm()
    evaluator.evaluate_knn(k=5)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    evaluator.plot_comparison()
    
    # Generate report
    evaluator.summary_report()
    
    print("\n" + "="*60)
    print("Evaluation Complete!")
    print("Check results/ directory for visualizations and report")
    print("="*60)


if __name__ == '__main__':
    main()
